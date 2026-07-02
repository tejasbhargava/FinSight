# FinSight 📈

**AI-Powered Financial Research Assistant**

FinSight is an end-to-end financial research platform that combines SEC filings, market data, financial news, Retrieval-Augmented Generation (RAG), and Large Language Models to help users perform company research, compare businesses, and generate structured investment theses — with full user authentication and persistent conversation history.

---

## Features

### User Authentication

Secure account system with:

* JWT-based authentication
* Bcrypt password hashing
* Protected API endpoints
* Per-user data isolation

Every research session, comparison, and report is tied to an authenticated user.

---

### Conversational Financial Research

Ask natural language questions about public companies.

Examples:

* What are Apple's biggest risks?
* How does NVIDIA generate revenue?
* What growth opportunities does Microsoft have?

FinSight retrieves relevant information from SEC filings, financial news, and market data before generating grounded responses. Conversations persist across sessions — ask a follow-up question days later and the assistant still has context.

---

### Persistent Conversation History

All conversations are stored in PostgreSQL and organized into chat sessions, ChatGPT-style:

* Every research query, comparison, and thesis generation creates or continues a session
* Full message history (user + assistant turns) is saved with timestamps
* Sessions can be reopened anytime — conversation history survives logout/login
* Sidebar displays all past sessions for quick access

---

### SEC Filing Analysis

FinSight automatically:

* Downloads SEC filings
* Parses filing content
* Chunks documents by section (Item 1, Item 1A, Item 7, etc.)
* Creates embeddings
* Stores vectors in FAISS

Supported filing types:

* 10-K
* 10-Q
* 8-K

---

### Retrieval-Augmented Generation (RAG)

The system uses:

* Section-aware document chunking
* HuggingFace Embeddings (BAAI/bge-base-en-v1.5)
* FAISS Vector Store
* MMR Retrieval
* Conversational Question Contextualization (standalone question rewriting using chat history)

This allows the assistant to answer questions using relevant filing excerpts instead of relying solely on LLM knowledge.

---

### Financial News Integration

Recent company news is incorporated into responses to provide context about:

* Product launches
* Partnerships
* Lawsuits
* Regulatory developments
* Market sentiment

---

### Stock Market Data Integration

FinSight retrieves live market information including:

* Current Price
* Market Capitalization
* PE Ratio
* EPS
* Revenue
* Net Income
* Dividend Yield
* Debt-to-Equity Ratio
* Return on Equity

---

### Company Comparison

Compare two companies side-by-side using:

* Financial metrics
* Recent developments
* SEC filing insights
* Business strengths and weaknesses

Comparisons are conversational — ask follow-up questions on the same comparison and the assistant retains context via session-based chat history.

Example:

Compare Apple and Microsoft's long-term growth opportunities.

---

### Investment Thesis Generator

Generate structured research reports including:

* Executive Summary
* Business Overview
* Competitive Advantages
* Growth Drivers
* Financial Snapshot
* Recent Developments
* Bull Case
* Bear Case
* Key Risks
* Long-Term Outlook
* Conclusion

Generated theses are automatically saved to the database and linked to the user's account.

---

### PDF Export

Investment theses can be exported as professional PDF reports for later review and sharing — without re-running the LLM or retrieval pipeline.

---

## System Architecture

User

↓

Streamlit Frontend (Auth + Chat UI)

↓

FastAPI Backend (JWT Protected)

↓

PostgreSQL ←→ Chat Sessions / Messages / Reports

↓

Research Pipeline

├── SEC Filing Retrieval

├── News Retrieval

├── Stock Data Retrieval

└── RAG Retrieval

↓

OpenRouter LLM

↓

Final Response (saved + returned)

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Pydantic

### Authentication

* JWT (python-jose)
* Bcrypt (passlib)

### Database

* PostgreSQL
* SQLAlchemy

### LLM & AI

* OpenRouter
* LangChain

### RAG

* HuggingFace Embeddings
* FAISS
* MMR Retrieval

### Data Sources

* SEC Filings
* Yahoo Finance
* Financial News APIs

### PDF Generation

* ReportLab

---

## Project Structure

```text
FinanceResearchAssistant/

backend/
│
├── auth/
│   ├── router.py
│   ├── dependencies.py
│   ├── schemas.py
│   ├── utils.py
│
├── db/
│   ├── database.py
│   ├── models.py
│
├── rag/
│   ├── ingestor.py
│   ├── retriever.py
│
├── tools/
│   ├── stock.py
│   ├── news.py
│   ├── filings.py
│
├── utils/
│   ├── ticker_lookup.py
│   ├── pdf_generator.py
│
├── agent.py
├── compare.py
├── thesis.py
├── main.py
├── schemas.py
├── llm.py
├── config.py
├── create_tables.py
│
Frontend/
│
├── app.py
│
requirements.txt
README.md
```

---

## Database Schema

```text
users
├── id, username, email, password_hash, created_at

chat_sessions
├── id, user_id (FK), company, title, created_at

messages
├── id, session_id (FK), role, content, tools_used, created_at

reports
├── id, user_id (FK), company, report_type, content, created_at
```

---

## Installation

Clone the repository:

```bash
git clone <your-repo-url>

cd FinanceResearchAssistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_key
NEWS_API_KEY=your_key
MODEL_NAME=your_model
DATABASE_URL=postgresql://username:password@localhost:5432/finsight_db
SECRET_KEY=your_random_secret_key
```

Create the database tables:

```bash
cd backend
python create_tables.py
```

---

## Running the Backend

```bash
cd backend

uvicorn main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

Use the **Authorize** button in Swagger to log in and test protected endpoints.

---

## Running the Frontend

```bash
cd Frontend

streamlit run app.py
```

---

## API Endpoints

### Authentication

```http
POST /auth/register
POST /auth/login
```

### Ingest SEC Filings

```http
POST /ingest
```

### Financial Research

```http
POST /query
```

### Company Comparison

```http
POST /compare
```

### Investment Thesis Generation

```http
POST /thesis
```

### PDF Export

```http
POST /thesis/pdf
```

### Conversation History

```http
GET /sessions
GET /sessions/{session_id}
```

---

## Example Workflow

1. Register an account and log in.
2. Ingest Apple's latest 10-K.
3. Ask questions about risks and strategy — conversation is saved automatically.
4. Compare Apple and Microsoft, with follow-up questions.
5. Generate an investment thesis.
6. Export the report as a PDF.
7. Log out, log back in — all conversation history is still there.

---

## Future Improvements

* Multi-company portfolio analysis
* Historical financial trend analysis
* Advanced citation support
* Refresh token rotation
* Docker deployment
* Cloud deployment
* Real-time market monitoring

---

## Screenshots
All Content couldnt be covered in the screenshots here are the main ones to get a preview of the project :)
<details>
<summary>🔐 Authentication</summary>

<br>

![Login](screenshots/login.png)

<br>

![Register](screenshots/register.png)

</details>

<details>
<summary>📊 Research Assistant</summary>

<br>

![Research 1](screenshots/research_assistant_1.png)

<br>

![Research 2](screenshots/research_assistant_2.png)

</details>

<details>
<summary>⚖️ Company Comparison</summary>

<br>

![Comparison 1](screenshots/comparision_1.png)

<br>

![Comparison 2](screenshots/comparision_2.png)

<br>

![Comparison 3](screenshots/comparision_3.png)

</details>

<details>
<summary>📝 Investment Thesis</summary>

<br>

![Thesis 1](screenshots/thesis_1.png)

<br>

![Thesis 2](screenshots/thesis_2.png)

<br>

![Thesis 2](screenshots/thesis_3.png)

</details>

<details>
<summary>🗂️ Conversation History</summary>

<br>

![History](screenshots/history.png)

</details>

<details>
<summary>🗂️ Evaluation</summary>

<br>

![History](screenshots/eval_ss.png)

</details>


## Disclaimer

This project is intended for educational and research purposes only.

It does not constitute financial or investment advice.