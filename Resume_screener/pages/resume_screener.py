import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfminer.high_level
from PIL import Image
import pytesseract
import sqlite3
import pandas as pd
import re
import plotly.graph_objects as go
#login app connect
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.switch_page("login.py")
#Configuration
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Page configuration
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Theme-Adaptive Cards */
    [data-testid="stMetric"] {
        background-color: rgba(151, 166, 195, 0.08); /* Adapts to background */
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .stMetric label {
        font-weight: 500 !important;
    }

    /* Skill Tags Styling - Better Colors for both modes */
    .skill-tag {
        display: inline-block;
        padding: 6px 14px;
        margin: 5px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .skill-match {
        background-color: rgba(16, 185, 129, 0.2);
        color: #059669; /* Darker green for readability on light */
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .skill-missing {
        background-color: rgba(239, 68, 68, 0.2);
        color: #dc2626; /* Darker red for readability on light */
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Hero Section - Fixed Dark Background for High Contrast */
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff !important;
        padding: 50px 20px;
        border-radius: 20px;
        margin-bottom: 40px;
        text-align: center;
        border: 1px solid #334155;
    }
    
    .hero-section h1 {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 10px;
        background: linear-gradient(to right, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        color: #ffffff; /* Fallback */
    }
    
    .hero-section p {
        color: #94a3b8 !important;
        font-size: 1.1rem;
    }

    /* Sidebar - Adaptive but refined */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Better Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #3b82f6, #8b5cf6);
    }
    
    /* Radar Chart Container */
    .plotly-graph-div {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        font-weight: 600;
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
    # Expanded skill library for professional analysis
    skill_categories = {
        "Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "php", "go", "rust", "kotlin", "swift", "sql", "ruby", "r"],
        "Web Tech": ["react", "angular", "vue", "node", "express", "fastapi", "django", "flask", "html", "css", "tailwind", "bootstrap"],
        "AI/ML": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv"],
        "Cloud/DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "linux", "terraform", "ansible"],
        "Data": ["postgresql", "mongodb", "redis", "elasticsearch", "spark", "hadoop", "tableau", "power bi", "excel", "bigquery"],
        "Soft Skills": ["leadership", "communication", "problem solving", "agile", "scrum", "project management", "teamwork", "critical thinking"]
    }
    
    # Flatten the list
    all_skills = [skill for sublist in skill_categories.values() for skill in sublist]
    
    jd_text_lower = jd_text.lower()
    # Use word boundary to avoid partial matches (e.g., "AI" in "Train")
    extracted = []
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_text_lower):
            extracted.append(skill)
            
    return sorted(list(set(extracted)))

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
    
    # Feature: Batch Processing (accept_multiple_files=True)
    uploaded_files = st.file_uploader("Upload Resume(s) (PDF)", type=["pdf"], accept_multiple_files=True)
    
    jd_option = st.radio("Job Description Source", ["Text", "Image"])
    job_desc = ""
    
    if jd_option == "Text":
        job_desc = st.text_area("Paste Job Description", height=200)
    else:
        uploaded_image = st.file_uploader("Upload JD Image", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            with st.spinner("Processing Image..."):
                extracted_text = pytesseract.image_to_string(image)
                job_desc = extracted_text.strip()
            if job_desc:
                st.success("Text Extracted from Image!")
            else:
                st.error("Could not extract text. Please ensure the image is clear.")

# Support function for Radar Chart
def create_radar_chart(matching_skills, missing_skills):
    categories = ['Match Score', 'Skill Match', 'Keyword Density', 'Profile Depth']
    
    # Heuristic scoring for visualization
    match_pct = (len(matching_skills) / (len(matching_skills) + len(missing_skills)) * 100) if (len(matching_skills) + len(missing_skills)) > 0 else 0
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[match_pct, len(matching_skills)*10, 70, 60], # Dummy values for demo depth
        theta=categories,
        fill='toself',
        name='Candidate Profile',
        line_color='#60a5fa'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=300
    )
    return fig

# Main Analysis Section
if uploaded_files and job_desc:
    results = []
    
    with st.spinner("Analyzing Resumes..."):
        for uploaded_file in uploaded_files:
            # 1. Extraction
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                # 2. Skill Extraction
                required_skills = extract_skills_from_jd(job_desc)
                if not required_skills:
                    required_skills = ["python", "data analysis", "machine learning"]
                
                matching_skills = [s for s in required_skills if s in resume_text.lower()]
                missing_skills = [s for s in required_skills if s not in resume_text.lower()]
                
                # 3. Similarity Score
                vectorizer = TfidfVectorizer()
                vectors = vectorizer.fit_transform([clean_text(resume_text), clean_text(job_desc)])
                score = cosine_similarity(vectors[0], vectors[1])[0][0] * 100
                
                results.append({
                    "Filename": uploaded_file.name,
                    "Score": score,
                    "Matched": matching_skills,
                    "Missing": missing_skills,
                    "Text": resume_text
                })
                
                # Save to DB
                save_to_db(uploaded_file.name, score, matching_skills, missing_skills)

        # 4. Ranking Leaderboard
        if results:
            # Sort results by score
            results = sorted(results, key=lambda x: x['Score'], reverse=True)
            
            st.subheader("🏆 Candidate Ranking")
            leaderboard_data = []
            for r in results:
                status = "✅ Top Match" if r['Score'] > 75 else "⚠️ Potential" if r['Score'] > 50 else "❌ Low Fit"
                leaderboard_data.append({
                    "Rank": results.index(r) + 1,
                    "Candidate": r['Filename'],
                    "Match Score": f"{r['Score']:.2f}%",
                    "Status": status
                })
            
            # Using dataframe for better look and scrollability
            st.dataframe(pd.DataFrame(leaderboard_data), width="stretch", hide_index=True)
            
            # Select Candidate for Detailed View
            selected_candidate_name = st.selectbox("🔍 Select Candidate for Detailed Analysis", [r['Filename'] for r in results])
            selected_data = next(item for item in results if item["Filename"] == selected_candidate_name)
        
        st.divider()
        st.header(f"Detailed Analysis: {selected_candidate_name}")
        
        # 5. Result Dashboard
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "🎯 Skill Analysis", "📜 Document Text", "🕒 History"])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric("Final Match Score", f"{selected_data['Score']:.2f}%")
                st.progress(int(selected_data['Score']))
                
                if selected_data['Score'] > 75:
                    st.success("High compatibility with requirements.")
                elif selected_data['Score'] > 50:
                    st.warning("Moderate match. Review recommended.")
                else:
                    st.error("Does not meet minimum criteria.")
            
            with col2:
                # Suggestion 4: Radar Chart
                st.write("**Visual Match Profile**")
                fig = create_radar_chart(selected_data['Matched'], selected_data['Missing'])
                st.plotly_chart(fig, width="stretch")

        with tab2:
            st.subheader("Keyword Matching")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Matched Skills**")
                if selected_data['Matched']:
                    tags = "".join([f'<span class="skill-tag skill-match">✅ {s}</span>' for s in selected_data['Matched']])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.write("None")
            with c2:
                st.markdown("**Missing Skills**")
                if selected_data['Missing']:
                    tags = "".join([f'<span class="skill-tag skill-missing">❌ {s}</span>' for s in selected_data['Missing']])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.write("None")
            
            # Smart Analysis (Local - 100% Reliable)
            st.divider()
            st.subheader("💡 Smart Recruitment Analysis")
            
            # Match Status
            if selected_data['Score'] > 80:
                st.success("🏆 **TOP TIER MATCH**: This candidate is an expert match in your technical stack.")
            elif selected_data['Score'] > 50:
                st.warning("⚖️ **BALANCED PROFILE**: Good alignment, though some skill gaps exist.")
            else:
                st.error("📉 **LOW MATCH**: Significant technical mismatches detected.")
                
            # Logic-based advice
            if selected_data['Missing']:
                st.info(f"**Interview Tip:** Focus questions on **{', '.join(selected_data['Missing'][:2])}** to gauge their ability to upskill.")
            else:
                st.success("**Interview Tip:** Candidate has all critical technical keywords. Focus on behavioral and culture fit.")

        with tab3:
            st.subheader("Extracted Content")
            with st.expander("Resume Text (Raw)"):
                st.text(selected_data['Text'][:2000] + "...")
            with st.expander("Job Description Source"):
                st.text(job_desc)

        with tab4:
            st.subheader("System Application History")
            conn = init_db()
            df_history = pd.read_sql_query("SELECT filename, score, matching_skills, timestamp FROM resumes ORDER BY timestamp DESC", conn)
            st.dataframe(df_history, width="stretch")
            conn.close()

else:
    st.write("---")
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    col1.markdown("1. **Upload Resume**\nUpload your professional CV in PDF format.")
    col2.markdown("2. **Paste JD**\nProvide the Job Description (Text or Image).")
    col3.markdown("3. **Get Insights**\nSee your score and missing skills instantly.")

