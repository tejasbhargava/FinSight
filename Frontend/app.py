import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FinSight",
    page_icon="📈",
    layout="wide"
)

# ---------------------------
# SESSION STATE
# ---------------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "sessions_list" not in st.session_state:
    st.session_state.sessions_list = []

if "page" not in st.session_state:
    st.session_state.page = "Research Chat"


# ---------------------------
# API HELPERS
# ---------------------------
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password},  # form-encoded, not JSON
            timeout=30
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            return True
        else:
            st.error("Invalid email or password.")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
        return False


def register(username: str, email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=30
        )
        if response.status_code == 200:
            return True
        else:
            st.error(response.json().get("detail", "Registration failed."))
            return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
        return False


def fetch_sessions():
    try:
        response = requests.get(f"{BASE_URL}/sessions", headers=auth_headers(), timeout=30)
        if response.status_code == 200:
            st.session_state.sessions_list = response.json()
        elif response.status_code == 401:
            logout()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")


def load_session(session_id: int):
    try:
        response = requests.get(f"{BASE_URL}/sessions/{session_id}", headers=auth_headers(), timeout=30)
        if response.status_code == 200:
            data = response.json()
            st.session_state.active_session_id = session_id
            st.session_state.chat_history = data["messages"]
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")


def send_query(company: str, question: str, session_id: int = None) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"company": company, "question": question, "session_id": session_id},
            headers=auth_headers(),
            timeout=90
        )
        if response.status_code == 401:
            logout()
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
    return None


def send_compare(company1: str, company2: str, question: str, session_id: int = None) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/compare",
            json={"company1": company1, "company2": company2, "question": question, "session_id": session_id},
            headers=auth_headers(),
            timeout=120
        )
        if response.status_code == 401:
            logout()
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
    return None


def send_thesis(company: str, session_id: int = None) -> dict:
    try:
        response = requests.post(
            f"{BASE_URL}/thesis",
            json={"company": company, "session_id": session_id},
            headers=auth_headers(),
            timeout=150
        )
        if response.status_code == 401:
            logout()
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
    return None


def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.active_session_id = None
    st.session_state.chat_history = []
    st.session_state.sessions_list = []
    st.rerun()


def new_chat():
    st.session_state.active_session_id = None
    st.session_state.chat_history = []


# ---------------------------
# AUTH SCREEN
# ---------------------------
def auth_screen():
    st.markdown("## 📈 FinSight")
    st.caption("AI-Powered Financial Research Assistant")
    st.divider()

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                with st.spinner("Logging in..."):
                    if login(email, password):
                        st.rerun()

    with tab2:
        username = st.text_input("Username", key="reg_username")
        email_r = st.text_input("Email", key="reg_email")
        password_r = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register", use_container_width=True):
            if not username or not email_r or not password_r:
                st.warning("Please fill all fields.")
            else:
                with st.spinner("Creating account..."):
                    if register(username, email_r, password_r):
                        st.success("Account created. Please log in.")


# ---------------------------
# SIDEBAR
# ---------------------------
def sidebar():
    with st.sidebar:
        st.markdown("## 📈 FinSight")
        st.caption("AI-Powered Financial Research Assistant")
        st.divider()

        st.session_state.page = st.radio(
            "Navigate",
            ["Research Chat", "Compare Companies", "Investment Thesis"],
            label_visibility="collapsed"
        )

        if st.button("➕ New Chat", use_container_width=True):
            new_chat()

        st.divider()
        st.markdown("**Conversation History**")

        fetch_sessions()

        if not st.session_state.sessions_list:
            st.caption("No conversations yet.")
        else:
            for s in st.session_state.sessions_list:
                label = s["title"] or s["company"] or "Untitled"
                if st.button(label, key=f"session_{s['id']}", use_container_width=True):
                    load_session(s["id"])
                    st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ---------------------------
# RESEARCH CHAT PAGE
# ---------------------------
def research_chat_page():
    st.title("🔍 Research Chat")

    company = st.text_input("Company", placeholder="e.g. Apple, Microsoft, Nvidia")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tools_used"):
                with st.expander("Tools Used"):
                    for t in msg["tools_used"]:
                        st.markdown(f"- `{t}`")

    question = st.chat_input("Ask a question about this company...")

    if question:
        if not company:
            st.warning("Please enter a company name first.")
        else:
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question, "tools_used": []})

            with st.chat_message("assistant"):
                with st.spinner("Analyzing company..."):
                    result = send_query(
                        company=company,
                        question=question,
                        session_id=st.session_state.active_session_id
                    )

                if result:
                    st.markdown(result["answer"])
                    st.session_state.active_session_id = result["session_id"]
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "tools_used": result.get("tools_used", [])
                    })

                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("🛠️ Tools Used"):
                            for t in result.get("tools_used", []):
                                st.markdown(f"- `{t}`")
                    with col2:
                        with st.expander("📄 Sources"):
                            for s in result.get("sources", []):
                                st.markdown(f"- `{s}`")


# ---------------------------
# COMPARE PAGE
# ---------------------------
def compare_page():
    st.title("⚖️ Compare Companies")

    col1, col2 = st.columns(2)
    with col1:
        company1 = st.text_input("Company 1", placeholder="e.g. Apple")
    with col2:
        company2 = st.text_input("Company 2", placeholder="e.g. Microsoft")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a comparison question...")

    if question:
        if not company1 or not company2:
            st.warning("Please enter both company names.")
        else:
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question, "tools_used": []})

            with st.chat_message("assistant"):
                with st.spinner("Comparing companies..."):
                    result = send_compare(
                        company1=company1,
                        company2=company2,
                        question=question,
                        session_id=st.session_state.active_session_id
                    )

                if result:
                    st.markdown(result["comparison"])
                    st.session_state.active_session_id = result["session_id"]
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["comparison"],
                        "tools_used": result.get("tools_used", [])
                    })

                    with st.expander("🛠️ Tools Used"):
                        for t in result.get("tools_used", []):
                            st.markdown(f"- `{t}`")


# ---------------------------
# THESIS PAGE
# ---------------------------
def thesis_page():
    st.title("📝 Investment Thesis")

    company = st.text_input("Company", placeholder="e.g. Nvidia, Tesla")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.button("Generate Thesis", use_container_width=True):
        if not company:
            st.warning("Please enter a company name.")
        else:
            user_note = f"Generate investment thesis for {company}"
            with st.chat_message("user"):
                st.markdown(user_note)
            st.session_state.chat_history.append({"role": "user", "content": user_note, "tools_used": []})

            with st.chat_message("assistant"):
                with st.spinner("Generating investment thesis..."):
                    result = send_thesis(
                        company=company,
                        session_id=st.session_state.active_session_id
                    )

                if result:
                    st.markdown(result["report"])
                    st.session_state.active_session_id = result["session_id"]
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["report"],
                        "tools_used": result.get("tools_used", [])
                    })

                    with st.expander("🛠️ Tools Used"):
                        for t in result.get("tools_used", []):
                            st.markdown(f"- `{t}`")


# ---------------------------
# MAIN
# ---------------------------
if not st.session_state.token:
    auth_screen()
else:
    sidebar()

    if st.session_state.page == "Research Chat":
        research_chat_page()
    elif st.session_state.page == "Compare Companies":
        compare_page()
    elif st.session_state.page == "Investment Thesis":
        thesis_page()