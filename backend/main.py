from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

import traceback
from fastapi.responses import FileResponse

# ==================================================
# APP
# ==================================================

app = FastAPI(
    title="FinSight",
    description="AI-Powered Financial Research Assistant",
    version="1.0.0"
)


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

@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["Research"]
)
def query(
    request: QueryRequest
):

    try:

        result = run_query(
            company=request.company,
            question=request.question,
            chat_history=request.chat_history
        )

        return QueryResponse(
            answer=result["answer"],
            tools_used=result["tools_used"],
            sources=result["sources"]
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
# COMPARE
# ==================================================

@app.post(
    "/compare",
    response_model=CompareResponse,
    tags=["Comparison"]
)
def compare(
    request: CompareRequest
):

    try:

        result = run_compare(
            company1=request.company1,
            company2=request.company2,
            question=request.question,
            chat_history=request.chat_history
        )

        return CompareResponse(
            comparison=result["comparison"],
            tools_used=result["tools_used"],
            sources=result["sources"]
        )

    except Exception as e:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post(
    "/thesis",
    response_model=ThesisResponse,
    tags=["Research Reports"]
)
def thesis(request: ThesisRequest):

    result = generate_investment_thesis(
        company=request.company,
        chat_history=request.chat_history
    )

    return ThesisResponse(
        report=result["report"],
        tools_used=result["tools_used"],
        sources=result["sources"]
    )

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