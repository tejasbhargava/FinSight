import streamlit as st
import requests

# ---------------------------
# CONFIG
# ---------------------------
BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FinSight",
    page_icon="📈",
    layout="wide"
)

# ---------------------------
# SESSION STATE
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "latest_report" not in st.session_state:
    st.session_state.latest_report = None

if "latest_company" not in st.session_state:
    st.session_state.latest_company = None

if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = None

if "last_query_answer" not in st.session_state:
    st.session_state.last_query_answer = None

if "last_ingest_result" not in st.session_state:
    st.session_state.last_ingest_result = None

# ---------------------------
# API LAYER
# ---------------------------
def query_company(company: str, question: str, chat_history: list) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "company": company,
                "question": question,
                "chat_history": chat_history
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out. The backend is taking too long.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure it is running on port 8000.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.json().get('detail', str(e))}")
    return None


def compare_companies(company1: str, company2: str, question: str) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/compare",
            json={
                "company1": company1,
                "company2": company2,
                "question": question
            },
            timeout=90
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.json().get('detail', str(e))}")
    return None


def generate_thesis(company: str) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/thesis",
            json={
                "company": company,
                "chat_history": []
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.json().get('detail', str(e))}")
    return None


def generate_pdf(company: str, report: str) -> bytes:
    try:
        response = requests.post(
            f"{BASE_URL}/thesis/pdf",
            json={
                "company": company,
                "report": report
            },
            timeout=60
        )
        response.raise_for_status()
        return response.content
    except requests.exceptions.Timeout:
        st.error("PDF generation timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {str(e)}")
    return None


def ingest_company(company: str, form_type: str) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/ingest",
            json={"company": company, "form_type": form_type},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Ingestion timed out. Large filings can take a while.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.json().get('detail', str(e))}")
    return None


# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("## 📈 FinSight")
    st.caption("AI-Powered Financial Research Assistant")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "🔍 Research Assistant",
            "⚖️ Company Comparison",
            "📝 Investment Thesis",
            "📂 SEC Filing Ingestion",
            "ℹ️ About"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Powered by SEC EDGAR · NewsAPI · Yahoo Finance")


# ---------------------------
# PAGE 1: RESEARCH ASSISTANT
# ---------------------------
if page == "🔍 Research Assistant":
    st.title("🔍 Research Assistant")
    st.caption("Ask anything about a company — powered by SEC filings, live stock data, and recent news.")
    st.divider()

    company = st.text_input(
        "Company",
        placeholder="e.g. Apple, Microsoft, Nvidia",
        key="research_company"
    )

    # display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # question input
    question = st.chat_input("Ask a question about this company...")

    if question:
        if not company:
            st.warning("Please enter a company name first.")
        else:
            # display user message
            with st.chat_message("user"):
                st.markdown(question)

            # append to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })

            # call backend
            with st.chat_message("assistant"):
                with st.spinner("Researching..."):
                    result = query_company(
                        company=company,
                        question=question,
                        chat_history=st.session_state.chat_history
                    )

                if result:
                    answer = result["answer"]
                    st.markdown(answer)

                    # persist
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                    st.session_state.last_query_answer = answer

                    # metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("🛠️ Tools Used"):
                            for t in result.get("tools_used", []):
                                st.markdown(f"- `{t}`")
                    with col2:
                        with st.expander("📄 Sources"):
                            for s in result.get("sources", []):
                                st.markdown(f"- `{s}`")

    # clear chat
    if st.session_state.chat_history:
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ---------------------------
# PAGE 2: COMPANY COMPARISON
# ---------------------------
elif page == "⚖️ Company Comparison":
    st.title("⚖️ Company Comparison")
    st.caption("Compare two companies across financials, risks, and recent developments.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        company1 = st.text_input("Company 1", placeholder="e.g. Apple")
    with col2:
        company2 = st.text_input("Company 2", placeholder="e.g. Microsoft")

    question = st.text_input(
        "Comparison Question",
        value="Compare these two companies across financials, risks, and recent news.",
        placeholder="What do you want to compare?"
    )

    if st.button("⚖️ Compare", use_container_width=True):
        if not company1 or not company2:
            st.warning("Please enter both company names.")
        else:
            with st.spinner(f"Comparing {company1} and {company2}..."):
                result = compare_companies(company1, company2, question)

            if result:
                st.session_state.last_comparison = result["comparison"]

                st.divider()
                st.subheader(f"{company1} vs {company2}")
                st.markdown(result["comparison"])

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("🛠️ Tools Used"):
                        for t in result.get("tools_used", []):
                            st.markdown(f"- `{t}`")
                with col2:
                    with st.expander("📄 Sources"):
                        for s in result.get("sources", []):
                            st.markdown(f"- `{s}`")

    # persist result across reruns
    elif st.session_state.last_comparison:
        st.divider()
        st.subheader("Last Comparison")
        st.markdown(st.session_state.last_comparison)


# ---------------------------
# PAGE 3: INVESTMENT THESIS
# ---------------------------
elif page == "📝 Investment Thesis":
    st.title("📝 Investment Thesis")
    st.caption("Generate a full investment research report for any company.")
    st.divider()

    company = st.text_input(
        "Company",
        placeholder="e.g. Nvidia, Tesla, Amazon"
    )

    if st.button("📝 Generate Thesis", use_container_width=True):
        if not company:
            st.warning("Please enter a company name.")
        else:
            with st.spinner(f"Generating investment thesis for {company}..."):
                result = generate_thesis(company)

            if result:
                st.session_state.latest_report = result["report"]
                st.session_state.latest_company = company

                st.divider()
                st.subheader(f"Investment Thesis — {company}")
                st.markdown(result["report"])

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("🛠️ Tools Used"):
                        for t in result.get("tools_used", []):
                            st.markdown(f"- `{t}`")
                with col2:
                    with st.expander("📄 Sources"):
                        for s in result.get("sources", []):
                            st.markdown(f"- `{s}`")

    # persist report across reruns
    elif st.session_state.latest_report:
        st.divider()
        st.subheader(f"Investment Thesis — {st.session_state.latest_company}")
        st.markdown(st.session_state.latest_report)

    # PDF export — only show if report exists
    if st.session_state.latest_report:
        st.divider()
        st.markdown("#### 📥 Export Report")

        if st.button("Generate PDF", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf(
                    company=st.session_state.latest_company,
                    report=st.session_state.latest_report
                )

            if pdf_bytes:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.latest_company}_Investment_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


# ---------------------------
# PAGE 4: SEC FILING INGESTION
# ---------------------------
elif page == "📂 SEC Filing Ingestion":
    st.title("📂 SEC Filing Ingestion")
    st.caption("Download and index a company's SEC filing for RAG retrieval.")
    st.divider()

    company = st.text_input(
        "Company",
        placeholder="e.g. Apple, Microsoft, Tesla"
    )

    form_type = st.selectbox(
        "Filing Type",
        ["10-K", "10-Q", "8-K"]
    )

    if st.button("📂 Ingest Filing", use_container_width=True):
        if not company:
            st.warning("Please enter a company name.")
        else:
            with st.spinner(f"Ingesting {form_type} for {company}... this may take a minute."):
                result = ingest_company(company, form_type)

            if result:
                st.session_state.last_ingest_result = result
                st.success(f"Successfully ingested {form_type} for {company}")

                col1, col2, col3 = st.columns(3)
                col1.metric("Status", result.get("status", "—").capitalize())
                col2.metric("Chunks Created", result.get("chunks", "—"))

    # persist last result
    elif st.session_state.last_ingest_result:
        r = st.session_state.last_ingest_result
        st.divider()
        st.markdown("**Last Ingestion Result**")
        col1, col2 = st.columns(2)
        col1.metric("Status", r.get("status", "—").capitalize())
        col2.metric("Chunks", r.get("chunks", "—"))


# ---------------------------
# PAGE 5: ABOUT
# ---------------------------
elif page == "ℹ️ About":
    st.title("ℹ️ About FinSight")
    st.caption("How it works under the hood.")
    st.divider()

    st.markdown("""
FinSight is an AI-powered financial research assistant that combines multiple data sources
and retrieval techniques to generate grounded, cited financial analysis.
""")

    st.divider()

    components = {
        "📥 SEC Filing Ingestion": "Downloads 10-K and 10-Q filings directly from SEC EDGAR using the public API. No authentication required. Filings are saved locally for processing.",
        "✂️ Section-Aware Chunking": "Instead of blindly splitting documents by token count, FinSight splits SEC filings by their natural sections (Item 1, Item 1A, Item 7, etc.) before chunking. Every chunk carries metadata about which section it came from.",
        "🔍 FAISS Vector Search": "Chunks are embedded using a sentence-transformer model and stored in a FAISS index on disk. Each company gets its own index, enabling fast similarity search at query time.",
        "📐 MMR Retrieval": "At query time, FinSight uses Maximum Marginal Relevance (MMR) search instead of plain similarity search — balancing relevance with diversity so retrieved chunks don't all say the same thing.",
        "📰 Financial News Analysis": "Recent news headlines and summaries are fetched from NewsAPI, giving the LLM awareness of current events, product launches, regulatory actions, and market sentiment.",
        "📊 Stock Data Integration": "Live stock data is fetched from Yahoo Finance via yfinance — including price, PE ratio, market cap, EPS, 52-week range, revenue, and more.",
        "📝 Investment Thesis Generation": "Combines all three data sources — filings, news, stock data — and prompts the LLM to generate a structured investment research report covering business overview, financials, risks, and outlook.",
        "📄 PDF Export": "Generated reports can be exported as professionally formatted PDFs without re-running the LLM — the report is stored in session state and passed directly to the PDF generation endpoint.",
        "⚡ FastAPI Backend": "All data fetching, RAG retrieval, and LLM orchestration runs in a FastAPI backend with clean endpoint separation and Pydantic request/response validation.",
        "🖥️ Streamlit Frontend": "The frontend is built with Streamlit, using session state to persist conversation history, reports, and comparison results across reruns."
    }

    for title, description in components.items():
        with st.expander(title):
            st.markdown(description)