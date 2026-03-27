import streamlit as st
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

st.title("AI Resume Screener")

# upload resume
uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

# job description
job_desc = st.text_area("job Description")

if uploaded_file and job_desc:

    # extract resume text
    resume_text = extract_text(uploaded_file)

    # TF-IDF
    documents = [resume_text, job_desc]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # cosine similarity
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    score = score * 100

    st.subheader("Match Score")
    st.write(f"{score:.2f}%")