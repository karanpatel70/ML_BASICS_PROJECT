import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfminer.high_level
from PIL import Image
import pytesseract

# ------------------ FUNCTION TO EXTRACT TEXT ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = pdfminer.high_level.extract_text(uploaded_file)
        return text if text else ""
    except:
        return ""

# ------------------ STREAMLIT UI ------------------
st.markdown("""
<div style="
    text-align: center;
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #ddd;
    margin-bottom: 20px;
">
    <h1 style="color:#333;">AI Resume Screener</h1>
</div>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])
    job_desc = st.text_area("Job Description")
    jd_option = st.radio("Job Description Input Type", ["Text", "Image"])
    job_desc = ""

if jd_option == "Text":
    job_desc = st.text_area("Enter Job Description")

else:
    uploaded_image = st.file_uploader("Upload Job Description Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        job_desc = pytesseract.image_to_string(image)

        st.subheader("Extracted Text")
        st.write(job_desc[:500])

# Default values
resume_text = ""
score = 0

# ------------------ MAIN LOGIC ------------------
if uploaded_file is not None and job_desc:
    
    # Extract resume text
    resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text.strip() != "":
        # Vectorization
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_desc])

        resume_vector = vectors[0]
        jd_vector = vectors[1]

        # Similarity score
        score = cosine_similarity(resume_vector, jd_vector)[0][0] * 100
# ------------------ RESULT SECTION ------------------
with col2:
    st.subheader("Result")
    st.metric("Match Score", f"{score:.2f}%")
    st.progress(int(score))

    if score > 70:
        st.success("Great Match!")
    elif score > 40:
        st.warning("Average Match")
    else:
        st.error("Poor Match")

# ------------------ SKILL ANALYSIS ------------------
skills = ["python", "data analysis", "machine learning", "problem solving"]

matching_skills = [skill for skill in skills if skill in resume_text.lower()]
missing_skills = [skill for skill in skills if skill not in resume_text.lower()]

col3, col4 = st.columns(2)

with col3:
    st.subheader("Matching Skills")
    for skill in matching_skills:
        st.write(f"✅ {skill}")

with col4:
    st.subheader("Missing Skills")
    for skill in missing_skills:
        st.write(f"❌ {skill}")

# ------------------ SUGGESTIONS ------------------
st.subheader("Suggestions")

for skill in missing_skills:
    st.write(f"Consider adding {skill} to your resume to improve your match score.")

# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["Analysis", "Raw Text"])

with tab1:
    st.write("Detailed analysis will go here.")

with tab2:
    if resume_text:
        st.write(resume_text[:500] + "...")