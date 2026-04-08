import streamlit as st
import pytesseract
from PIL import Image
import pdfminer.high_level
import pdfminer.high_level
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.markdown("""<style> ... </style>""", unsafe_allow_html=True)

# 🔥 CUSTOM CSS
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1, h2, h3 {
    text-align: center;
    font-weight: 700;
}

/* Input fields */
.stTextInput input {
    border-radius: 10px;
    padding: 10px;
    border: 2px solid #00c6ff;
    background-color: #1e2a38;
    color: white;
}

/* File uploader */
.stFileUploader {
    border: 2px dashed #00c6ff;
    padding: 10px;
    border-radius: 12px;
    background-color: #1e2a38;
}

/* Buttons */
.stButton button {
    background: linear-gradient(45deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    background: linear-gradient(45deg, #0072ff, #00c6ff);
}

/* Cards */
.card {
    background-color: #1e2a38;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.5);
    margin: 10px;
}

/* Success box */
.success-box {
    background-color: #0f5132;
    padding: 15px;
    border-radius: 10px;
}

/* Error box */
.error-box {
    background-color: #842029;
    padding: 15px;
    border-radius: 10px;
}

/* Hover animation */
.card:hover {
    transform: translateY(-5px);
    transition: 0.3s;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #00c6ff;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

#light toggle
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

toggle = st.toggle("🌗 Dark Mode", value=(st.session_state.theme == "dark"))

if toggle:
    st.session_state.theme = "dark"
else:
    st.session_state.theme = "light"

if st.session_state.theme == "dark":
    bg = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    card = "#1e2a38"
    text = "white"
else:
    bg = "#f5f7fa"
    card = "white"
    text = "black"

st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
    font-family: 'Segoe UI', sans-serif;
}}

.card {{
    background-color: {card};
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    margin: 10px;
}}

.skill-bar {{
    background: #444;
    border-radius: 10px;
    overflow: hidden;
}}

.skill-fill {{
    height: 10px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
}}

</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    pdf_file = BytesIO(uploaded_file.read())  # convert to file-like object
    text = pdfminer.high_level.extract_text(pdf_file)  # correct function
    return text

# if "logged_in" not in st.session_state or not st.session_state.logged_in:
#     st.warning("Please login first")
#     st.stop()
#     if st.sidebar.button("Logout"):
#         st.session_state.logged_in = False
#         st.switch_page("login.py")
#title
st.markdown("<h1> AI Resume Advisor</h1>", unsafe_allow_html=True)
#title and input
uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])
goal = st.text_input("Enter your career goal (e.g. AI/ML Engineer)")

career_skills = {
    "ai/ml engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch"],
    "data analyst": ["python", "sql", "data analysis", "excel", "power bi"],
    "web developer": ["html", "css", "javascript", "react", "node"]
}
#core logic
def get_similarity(resume_text, skills):
    results = {}

    for skill in skills:
        vectorizer = TfidfVectorizer()

        vectors = vectorizer.fit_transform([resume_text, skill])

        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

        results[skill] = similarity

    return results
#matching logic
matched = []
missing = []
resume_text = extract_text_from_pdf(uploaded_file)
goal = goal.lower().strip()

if uploaded_file and goal:

    resume_text = extract_text_from_pdf(uploaded_file)
    goal_skills = []

for key in career_skills:
    if key in goal:
        goal_skills = career_skills[key]
        break
    similarity_scores = get_similarity(resume_text, goal_skills)

    matched = [skill for skill, score in similarity_scores.items() if score > 0.1]
    missing = [skill for skill, score in similarity_scores.items() if score <= 0.1]

    st.markdown(f"<h3>🎯 Goal: {goal}</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ✅ Matched Skills")
        for s in matched:
            st.markdown(f"<div class='success-box'>✔ {s}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ❌ Missing Skills")
        for s in missing:
            st.markdown(f"<div class='error-box'>✘ {s}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
#results
    st.subheader("Career Goal")
    st.write(goal)

#suggestions
skill_advice = {
    "python": {
        "why": "Python is the core language for AI/ML and data work.",
        "learn": "Basics → NumPy → Pandas",
        "project": "Build a data analysis project using Pandas"
    },
    "machine learning": {
        "why": "ML helps you build intelligent systems.",
        "learn": "Supervised learning → regression → classification",
        "project": "Build a spam email classifier"
    },
    "deep learning": {
        "why": "Used in advanced AI like image and speech recognition.",
        "learn": "Neural networks → CNN → TensorFlow/PyTorch",
        "project": "Build an image classifier"
    },
    "sql": {
        "why": "Used to handle and query data efficiently.",
        "learn": "SELECT → JOIN → GROUP BY",
        "project": "Build a database system"
    },
    "react": {
        "why": "Helps build modern web interfaces.",
        "learn": "Components → Hooks → State",
        "project": "Build a portfolio website"
    }
}
#ui suggestions
st.markdown("## 🚀 Smart Suggestions")

for skill in missing:
    if skill in skill_advice:
        advice = skill_advice[skill]

        st.markdown(f"""
        <div class="card">
            <h4>📌 {skill.upper()}</h4>
            <p><b>Why:</b> {advice['why']}</p>
            <p><b>What to Learn:</b> {advice['learn']}</p>
            <p><b>Project Idea:</b> 💡 {advice['project']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"👉 Start learning {skill}")

for skill in missing:
    st.write(f"👉 Learn {skill}")

if not missing:
    st.warning("⚠️ No suggestions found. Try a clearer goal like 'AI/ML Engineer'")


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
