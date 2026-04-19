import streamlit as st
import requests

st.set_page_config(page_title="CVBoost AI", layout="wide")

API_URL = "http://127.0.0.1:8000"

# =========================
# SESSION STATE
# =========================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "email" not in st.session_state:
    st.session_state.email = None


# =========================
# SAFE JSON PARSER
# =========================
def safe_json(response):
    try:
        return response.json()
    except:
        return {"error": response.text}


# =========================
# AUTH FUNCTIONS
# =========================
def register(email, password):
    return requests.post(
        f"{API_URL}/register",
        data={"email": email, "password": password}
    )


def login(email, password):
    return requests.post(
        f"{API_URL}/login",
        data={"email": email, "password": password}
    )


# =========================
# LOGIN / REGISTER SCREEN
# =========================
if st.session_state.user_id is None:

    st.title("🚀 CVBoost AI")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # -------- LOGIN --------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            res = login(email, password)
            data = safe_json(res)

            st.write("Status:", res.status_code)  # debug

            if res.status_code == 200 and "user_id" in data:
                st.session_state.user_id = data["user_id"]
                st.session_state.email = data["email"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(data.get("detail", data.get("error", "Login failed")))

    # -------- REGISTER --------
    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")

        if st.button("Create Account"):
            res = register(email, password)
            data = safe_json(res)

            if res.status_code == 200:
                st.success("Account created! Please login.")
            else:
                st.error(data.get("detail", data.get("error", "Error")))

    st.stop()


# =========================
# MAIN APP (LOGGED IN)
# =========================
st.title("🚀 CVBoost AI Dashboard")
st.caption(f"Logged in as: {st.session_state.email}")

if st.button("Logout"):
    st.session_state.user_id = None
    st.session_state.email = None
    st.rerun()

st.divider()

# =========================
# CV OPTIMIZER
# =========================
st.subheader("📄 CV Optimizer")

uploaded_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])
job_description = st.text_area("Paste Job Description")

if st.button("Optimize CV"):

    if uploaded_file and job_description:

        with st.spinner("Analyzing CV..."):

            response = requests.post(
                f"{API_URL}/optimize-cv",
                files={"file": uploaded_file},
                data={
                    "job_description": job_description,
                    "user_id": st.session_state.user_id
                }
            )

            data = safe_json(response)

            if response.status_code == 200 and "result" in data:

                result = data["result"]

                st.success("Analysis Complete 🚀")

                st.metric("Match Score", f"{result['match_score']}%")

                st.write("### 🧠 Missing Skills")
                st.write(result["missing_skills"])

                st.write("### ✍️ Summary")
                st.write(result["summary_rewrite"])

                st.write("### 💡 Suggestions")
                st.write(result["improvement_suggestions"])

                st.write("### 📄 Cover Letter")
                st.text_area("", result["cover_letter"], height=200)

            else:
                st.error(data.get("error", "Backend error"))


# =========================
# HISTORY
# =========================
st.divider()
st.subheader("📊 My CV History")

if st.button("Load History"):

    response = requests.get(
        f"{API_URL}/history/{st.session_state.user_id}"
    )

    data = safe_json(response)

    if response.status_code == 200 and "history" in data:

        history = data["history"]

        if len(history) == 0:
            st.info("No history yet.")

        for item in reversed(history):

            with st.expander(f"📄 {item['filename']} — {item['match_score']}%"):

                st.write("🧠 Missing Skills")
                st.write(item["missing_skills"])

                st.write("✍️ Summary")
                st.write(item["summary"])

                st.write("📄 Cover Letter")
                st.write(item["cover_letter"])

                st.write("🕒 Date")
                st.write(item["created_at"])

    else:
        st.error(data.get("error", "Failed to load history"))