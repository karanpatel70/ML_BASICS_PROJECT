import streamlit as st
import pytesseract
from PIL import Image
import pdfminer.high_level
import pdfminer.high_level
from io import BytesIO



def extract_text_from_pdf(uploaded_file):
    pdf_file = BytesIO(uploaded_file.read())  # convert to file-like object
    text = pdfminer.high_level.extract_text(pdf_file)  # correct function
    return text

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()
#title
st.title("AI Resume Screener - Resume Advisor")
#title and input
st.title("Resume Advisor 🎯")
uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])
goal = st.text_input("Enter your career goal (e.g. AI/ML Engineer)")

career_skills = {
    "ai/ml engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch"],
    "data analyst": ["python", "sql", "data analysis", "excel", "power bi"],
    "web developer": ["html", "css", "javascript", "react", "node"]
}
matched = []
missing = []
if uploaded_file and goal:

    resume_text = extract_text_from_pdf(uploaded_file)

    goal_skills = career_skills.get(goal.lower(), [])

    matched = [s for s in goal_skills if s in resume_text.lower()]
    missing = [s for s in goal_skills if s not in resume_text.lower()]

    # results
    st.subheader("Career Goal")
    st.write(goal)

    st.subheader("Skill Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.success("Matched Skills")
        for s in matched:
            st.write(f"✅ {s}")

    with col2:
        st.error("Missing Skills")
        for s in missing:
            st.write(f"❌ {s}")
#results
    st.subheader("Career Goal")
    st.write(goal)
st.subheader("Skill Analysis")

col1, col2 = st.columns(2)

with col1:
        st.success("Matched Skills")
        for s in matched:
            st.write(f"✅ {s}")

with col2:
        st.error("Missing Skills")
        for s in missing:
            st.write(f"❌ {s}")
st.subheader("Suggestions")

for skill in missing:
    st.write(f"👉 Learn {skill}")

project_ideas = {
    "machine learning": "Build a spam classifier",
    "deep learning": "Create image classifier using CNN",
    "sql": "Build a database project",
    "react": "Build a portfolio website"
}

st.subheader("Project Ideas")

for skill in missing:
    if skill in project_ideas:
        st.write(f"💡 {project_ideas[skill]}")

st.subheader("Learning roadmap")

for i, skill in enumerate(missing, 1):
    st.write(f"{i}. Learn {skill}")