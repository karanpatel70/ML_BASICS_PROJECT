import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfminer.high_level
from PIL import Image
import pytesseract
import sqlite3
import pandas as pd
import re

# Page configuration
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .skill-tag {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .skill-match {
        background-color: #def7ec;
        color: #03543f;
        border: 1px solid #84e1bc;
    }
    .skill-missing {
        background-color: #fde8e8;
        color: #9b1c1c;
        border: 1px solid #f8b4b4;
    }
    .hero-section {
        background-color: #000000;
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ DATABASE HELPERS ------------------
def init_db():
    conn = sqlite3.connect("resume_data.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        score REAL,
        matching_skills TEXT,
        missing_skills TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Migration: Add timestamp column if it doesn't exist
    cursor.execute("PRAGMA table_info(resumes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "timestamp" not in columns:
        # Avoid DEFAULT CURRENT_TIMESTAMP in ALTER TABLE as it fails on some SQLite versions
        cursor.execute("ALTER TABLE resumes ADD COLUMN timestamp DATETIME")
        
    conn.commit()
    return conn

def save_to_db(filename, score, matched, missing):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO resumes (filename, score, matching_skills, missing_skills, timestamp)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (filename, score, ",".join(matched), ",".join(missing)))
    conn.commit()
    conn.close()

# ------------------ LOGIC HELPERS ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = pdfminer.high_level.extract_text(uploaded_file)
        return text if text else ""
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return ""

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def extract_skills_from_jd(jd_text):
    # A simple list of common tech skills for demonstration
    # In a production app, this could be a larger dictionary or an NLP-based extractor
    skill_library = [
        "python", "java", "javascript", "react", "node", "sql", "mongodb",
        "machine learning", "data science", "deep learning", "nlp", "aws",
        "docker", "kubernetes", "problem solving", "communication", "leadership",
        "tableau", "power bi", "excel", "c++", "c#", "php", "html", "css"
    ]
    jd_text_lower = jd_text.lower()
    extracted = [skill for skill in skill_library if skill in jd_text_lower]
    return extracted

# ------------------ UI LAYOUT ------------------

# Hero Header
st.markdown("""
<div class="hero-section">
    <h1>Smart AI Resume Screener</h1>
    <p>Optimize your hiring process with AI-driven matching and skill analysis.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for Inputs
with st.sidebar:
    st.header("📂 Dashboard")
    st.info("Upload materials below to start analysis.")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    jd_option = st.radio("Job Description Source", ["Text", "Image"])
    job_desc = ""
    
    if jd_option == "Text":
        job_desc = st.text_area("Paste Job Description", height=200)
    else:
        uploaded_image = st.file_uploader("Upload JD Image", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            with st.spinner("Processing Image..."):
                job_desc = pytesseract.image_to_string(image)
            st.success("Text Extracted from Image!")

# Main Analysis Section
if uploaded_file and job_desc:
    with st.spinner("Analyzing Resume..."):
        # 1. Extraction
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if resume_text:
            # 2. Skill Extraction (Dynamic)
            required_skills = extract_skills_from_jd(job_desc)
            if not required_skills:
                 # Fallback if no specific skills found, use hardcoded ones for demo
                 required_skills = ["python", "data analysis", "machine learning", "problem solving"]
            
            matching_skills = [s for s in required_skills if s in resume_text.lower()]
            missing_skills = [s for s in required_skills if s not in resume_text.lower()]
            
            # 3. Similarity Score
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([clean_text(resume_text), clean_text(job_desc)])
            score = cosine_similarity(vectors[0], vectors[1])[0][0] * 100
            
            # 4. Result Dashboard
            tab1, tab2, tab3 = st.tabs(["📊 Analysis Result", "📜 Extract Text", "🕒 History"])
            
            # Save current result once (using session state to avoid duplicates on reruns)
            current_id = f"{uploaded_file.name}_{len(job_desc)}_{score}"
            if "last_processed" not in st.session_state or st.session_state.last_processed != current_id:
                save_to_db(uploaded_file.name, score, matching_skills, missing_skills)
                st.session_state.last_processed = current_id

            with tab1:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("Match Score", f"{score:.2f}%")
                    if score > 75:
                        st.balloons()
                        st.success("Top Talent Detected!")
                    elif score > 50:
                        st.warning("Potential Match")
                    else:
                        st.error("Low Match")
                        
                    st.progress(int(score))
                
                with col2:
                    st.subheader("Skills Analysis")
                    st.markdown("**Matched Skills:**")
                    if matching_skills:
                        tags = "".join([f'<span class="skill-tag skill-match">✅ {s}</span>' for s in matching_skills])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.write("No matching skills found.")
                        
                    st.markdown("<br>**Missing Skills:**", unsafe_allow_html=True)
                    if missing_skills:
                        tags = "".join([f'<span class="skill-tag skill-missing">❌ {s}</span>' for s in missing_skills])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.write("No missing skills! Perfect match on keywords.")

                    # Suggestions
                    if missing_skills:
                        st.markdown("### 💡 Suggestions")
                        suggestion_list = list(missing_skills)[:3]
                        for s in suggestion_list:
                            st.info(f"Adding experience with **{s}** could boost your score.")

            with tab2:
                st.subheader("Extracted Content")
                with st.expander("Resume Text (First 1000 chars)"):
                    st.text(resume_text[:1000] + "...")
                with st.expander("Job Description"):
                    st.text(job_desc)

            with tab3:
                st.subheader("Recent Applications")
                # Fetch and display
                conn = init_db()
                df_history = pd.read_sql_query("SELECT filename, score, matching_skills, timestamp FROM resumes ORDER BY timestamp DESC", conn)
                st.dataframe(df_history, use_container_width=True)
                conn.close()
        else:
            st.error("Could not extract text from the PDF. Please ensure it's not a scanned image.")

else:
    st.write("---")
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    col1.markdown("1. **Upload Resume**\nUpload your professional CV in PDF format.")
    col2.markdown("2. **Paste JD**\nProvide the Job Description (Text or Image).")
    col3.markdown("3. **Get Insights**\nSee your score and missing skills instantly.")