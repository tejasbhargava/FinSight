from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user

from backend.db.database import get_db

from backend.db.model import (
    Report,
    User,
    ChatSession,
    Message
)

from backend.schemas import (
    QueryRequest,
    QueryResponse,
    CompareRequest,
    CompareResponse,
    IngestRequest,
    IngestResponse,
    ThesisRequest,
    ThesisResponse,
    PDFRequest
)


from backend.agent import run_query
from backend.compare import run_compare

from backend.rag.ingest import ingest_filing
from backend.utils.ticker_lookup import company_to_ticker

from backend.thesis import generate_investment_thesis
from backend.utils.pdf_generator import generate_pdf

from backend.auth.router import router as auth_router

import traceback
from fastapi.responses import FileResponse


from typing import List
# ==================================================
# APP
# ==================================================

app = FastAPI(
    title="FinSight",
    description="AI-Powered Financial Research Assistant",
    version="1.0.0"
)

app.include_router(auth_router)

# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# ROOT
# ==================================================

@app.get("/", tags=["System"])
def root():

    return {
        "name": "FinSight",
        "version": "1.0.0",
        "status": "running"
    }


# ==================================================
# HEALTH
# ==================================================

@app.get("/health", tags=["System"])
def health():

    return {
        "status": "ok"
    }


# ==================================================
# INGEST
# ==================================================

@app.post(
    "/ingest",
    response_model=IngestResponse,
    tags=["Ingestion"]
)
def ingest(
    request: IngestRequest
):

    try:

        info = company_to_ticker(
            request.company
        )

        ticker = info["ticker"]

        chunks = ingest_filing(
            ticker=ticker,
            form_type=request.form_type
        )

        return IngestResponse(
            status="success",
            ticker=ticker,
            chunks=chunks
        )

    except Exception as e:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# QUERY
# ==================================================

@app.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # step 1: get or create chat session
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()

            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = ChatSession(
                user_id=current_user.id,
                company=request.company,
                title=request.question[:50]
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # step 2: load previous messages in this session BEFORE adding the new one
        previous_messages = (
            db.query(Message)
            .filter(Message.session_id == session.id)
            .order_by(Message.created_at)
            .all()
        )

        chat_history = [
            {"role": m.role, "content": m.content}
            for m in previous_messages
        ]

        # step 3: save user's new message
        user_message = Message(
            session_id=session.id,
            role="user",
            content=request.question
        )
        db.add(user_message)

        # step 4: run the agent WITH chat history
        result = run_query(
            company=request.company,
            question=request.question,
            chat_history=chat_history
        )

        # step 5: save assistant's message
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=result["answer"],
            tools_used=",".join(result["tools_used"])
        )
        db.add(assistant_message)

        db.commit()

        return QueryResponse(
            answer=result["answer"],
            tools_used=result["tools_used"],
            sources=result["sources"],
            session_id=session.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# COMPARE
# ==================================================

@app.post("/compare", response_model=CompareResponse)
def compare(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # step 1: get or create chat session
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session_title = f"{request.company1} vs {request.company2}"
            session = ChatSession(
                user_id=current_user.id,
                company=session_title,
                title=session_title
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # step 2: load previous messages BEFORE adding the new one
        previous_messages = (
            db.query(Message)
            .filter(Message.session_id == session.id)
            .order_by(Message.created_at)
            .all()
        )
        chat_history = [{"role": m.role, "content": m.content} for m in previous_messages]

        # step 3: save user's question
        user_message = Message(
            session_id=session.id,
            role="user",
            content=request.question
        )
        db.add(user_message)

        # step 4: run comparison WITH chat history
        result = run_compare(
            company1=request.company1,
            company2=request.company2,
            question=request.question,
            chat_history=chat_history
        )

        # step 5: save assistant's response
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=result["comparison"],
            tools_used=",".join(result["tools_used"])
        )
        db.add(assistant_message)

        # step 6: also save to reports table
        report = Report(
            user_id=current_user.id,
            company=f"{request.company1} vs {request.company2}",
            report_type="comparison",
            content=result["comparison"]
        )
        db.add(report)

        db.commit()

        return CompareResponse(
            comparison=result["comparison"],
            tools_used=result["tools_used"],
            sources=result["sources"],
            session_id=session.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/thesis", response_model=ThesisResponse)
def thesis(
    request: ThesisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # step 1: get or create chat session
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = ChatSession(
                user_id=current_user.id,
                company=request.company,
                title=f"Investment Thesis — {request.company}"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # step 2: load previous messages BEFORE adding the new one
        previous_messages = (
            db.query(Message)
            .filter(Message.session_id == session.id)
            .order_by(Message.created_at)
            .all()
        )
        chat_history = [{"role": m.role, "content": m.content} for m in previous_messages]

        # step 3: save synthetic user message
        user_message = Message(
            session_id=session.id,
            role="user",
            content=f"Generate investment thesis for {request.company}"
        )
        db.add(user_message)

        # step 4: run thesis generation WITH chat history
        result = generate_investment_thesis(
            company=request.company,
            chat_history=chat_history
        )

        # step 5: save assistant's response
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=result["report"],
            tools_used=",".join(result["tools_used"])
        )
        db.add(assistant_message)

        # step 6: also save to reports table
        report = Report(
            user_id=current_user.id,
            company=request.company,
            report_type="thesis",
            content=result["report"]
        )
        db.add(report)

        db.commit()

        return ThesisResponse(
            report=result["report"],
            tools_used=result["tools_used"],
            sources=result["sources"],
            session_id=session.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/thesis/pdf",
    tags=["Research Reports"]
)
def export_pdf(
    request: PDFRequest
):

    try:

        pdf_path = generate_pdf(
            company=request.company,
            report=request.report
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{request.company}_Investment_Report.pdf"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/sessions")
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    return [
        {
            "id": s.id,
            "title": s.title,
            "company": s.company,
            "created_at": s.created_at
        }
        for s in sessions
    ]


@app.get("/sessions/{session_id}")
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )

    return {
        "session_id": session.id,
        "title": session.title,
        "company": session.company,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "tools_used": m.tools_used.split(",") if m.tools_used else []
            }
            for m in messages
        ]
    }
# ==================================================
# STARTUP
# ==================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )