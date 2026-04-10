import os
import re
from io import BytesIO

import pdfminer.high_level
import streamlit as st


st.set_page_config(page_title="AI Resume Advisor", page_icon="AI", layout="wide")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDepyqmcOhdJUbxjAuOOyWvyfDpsrOLD0k")
MODEL_CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-pro",
]

SKILL_LIBRARY = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c++", "sql", "r", "go"
    ],
    "Web": [
        "html", "css", "react", "node", "express", "django", "flask", "fastapi"
    ],
    "Data": [
        "pandas", "numpy", "power bi", "tableau", "excel", "statistics", "etl"
    ],
    "AI/ML": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "opencv"
    ],
    "Cloud/DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux"
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving", "agile"
    ],
}

GOAL_TEMPLATES = {
    "ai/ml engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "sql", "git"],
    "data analyst": ["python", "sql", "excel", "power bi", "tableau", "statistics", "pandas"],
    "data scientist": ["python", "sql", "machine learning", "statistics", "pandas", "numpy", "data visualization"],
    "web developer": ["html", "css", "javascript", "react", "node", "git"],
    "backend developer": ["python", "java", "sql", "api", "django", "flask", "docker"],
    "frontend developer": ["html", "css", "javascript", "react", "typescript", "git"],
}


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Your session is missing user details. Please login again.")
    st.session_state.logged_in = False
    st.switch_page("login.py")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.switch_page("login.py")


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #10243f 45%, #12385d 100%);
        color: #e5eefc;
    }
    .hero-card, .panel-card {
        background: rgba(8, 18, 33, 0.72);
        border: 1px solid rgba(148, 197, 255, 0.18);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(8px);
    }
    .hero-card h1 {
        margin-bottom: 0.4rem;
        color: #f8fbff;
        font-size: 2.6rem;
        font-weight: 800;
    }
    .hero-card p {
        color: #c3d7f2;
        font-size: 1rem;
        line-height: 1.7;
    }
    .chip {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        margin: 0.2rem;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .chip-good {
        background: rgba(16, 185, 129, 0.18);
        color: #7df0c2;
        border: 1px solid rgba(16, 185, 129, 0.32);
    }
    .chip-gap {
        background: rgba(248, 113, 113, 0.15);
        color: #ffb0b0;
        border: 1px solid rgba(248, 113, 113, 0.28);
    }
    .roadmap-box {
        background: rgba(6, 15, 29, 0.82);
        border: 1px solid rgba(96, 165, 250, 0.22);
        border-radius: 18px;
        padding: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    try:
        uploaded_file.seek(0)
        pdf_file = BytesIO(uploaded_file.read())
        text = pdfminer.high_level.extract_text(pdf_file)
        uploaded_file.seek(0)
        return text.strip() if text else ""
    except Exception as exc:
        st.error(f"Error extracting PDF text: {exc}")
        return ""


def normalize_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def detect_resume_skills(resume_text):
    lower_text = (resume_text or "").lower()
    found = []

    for category_skills in SKILL_LIBRARY.values():
        for skill in category_skills:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pattern, lower_text):
                found.append(skill)

    return sorted(set(found))


def expected_skills_for_goal(goal):
    lowered_goal = (goal or "").lower().strip()
    for goal_name, skills in GOAL_TEMPLATES.items():
        if goal_name in lowered_goal:
            return skills
    return []


def build_gap_summary(resume_skills, goal_skills):
    matched = [skill for skill in goal_skills if skill in resume_skills]
    missing = [skill for skill in goal_skills if skill not in resume_skills]
    return matched, missing


def generate_local_roadmap(goal, matched_skills, missing_skills):
    matched_text = ", ".join(matched_skills[:6]) if matched_skills else "No strong matches detected yet."
    missing_text = ", ".join(missing_skills[:8]) if missing_skills else "Your core goal skills already appear in the resume."

    return f"""
## Profile Summary
- Target role: {goal}
- Strong areas: {matched_text}
- Gaps to close: {missing_text}

## Step 1: Strengthen Foundations
- Review the role requirements and identify the top 5 recurring skills for {goal}.
- Refresh the basics of the missing topics before moving to advanced projects.
- Create short notes for concepts, formulas, syntax, and interview explanations.

## Step 2: Build Practical Skills
- Pick 2 missing skills and spend one focused week on each.
- For every skill, complete one tutorial and one hands-on exercise.
- Track what you learned in a weekly progress log.

## Step 3: Create Portfolio Proof
- Build 2 projects aligned with the target role.
- Write README files explaining the problem, your approach, and the result.
- Add those projects to your resume and LinkedIn profile.

## Step 4: Improve Resume Positioning
- Rewrite your summary to match the {goal} role.
- Move relevant projects, tools, and measurable achievements higher.
- Add keywords naturally so recruiters can quickly see alignment.

## Step 5: Prepare for Interviews
- Practice explaining each project in a structured way: problem, action, result.
- Prepare technical questions around your missing skills.
- Schedule mock interviews and refine weak areas after each attempt.

## Weekly Plan
1. Week 1-2: Foundations and concept revision.
2. Week 3-4: Build one guided project.
3. Week 5-6: Build one independent project.
4. Week 7: Update resume, GitHub, and LinkedIn.
5. Week 8: Interview practice and final gap review.
"""


def generate_ai_roadmap(resume_text, goal, matched_skills, missing_skills):
    try:
        from google import genai
    except ImportError:
        return None, "Gemini SDK is not installed. Install `google-genai` to enable AI roadmap generation."

    if not GEMINI_API_KEY:
        return None, "Gemini API key not found. Set `GEMINI_API_KEY` to enable AI roadmap generation."

    resume_excerpt = normalize_text(resume_text)[:12000]
    matched_text = ", ".join(matched_skills) if matched_skills else "No clear matching skills detected."
    missing_text = ", ".join(missing_skills) if missing_skills else "No obvious skill gaps detected from the template."

    prompt = f"""
You are an expert career coach and resume reviewer.

Analyze the candidate's resume and career goal, then produce a practical, detailed roadmap.

Candidate goal: {goal}
Already visible strengths: {matched_text}
Likely gaps: {missing_text}

Resume text:
{resume_excerpt}

Return the answer in Markdown with these exact sections:
## Goal Fit Summary
## Current Strengths
## Critical Gaps
## Step-by-Step Roadmap
## 30-60-90 Day Plan
## Best Projects To Build
## Resume Improvements
## Interview Preparation

Requirements:
- Be specific and actionable.
- Use numbered steps inside the roadmap.
- Mention tools, topics, and project ideas relevant to the target role.
- Include realistic sequencing from beginner to job-ready.
- Keep it detailed but easy to follow.
- If the resume looks weak in an area, say so clearly and explain how to improve it.
"""

    client = genai.Client(api_key=GEMINI_API_KEY)
    errors = []

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = getattr(response, "text", "") or ""
            if text.strip():
                return text, None
            errors.append(f"{model_name}: empty response")
        except Exception as exc:
            errors.append(f"{model_name}: {exc}")

    return None, "Gemini roadmap generation is unavailable right now, so a local roadmap is shown instead."


st.markdown(
    f"""
    <div class="hero-card">
        <h1>AI Resume Advisor</h1>
        <p>
            Upload your resume, tell the app your future role, and get a step-by-step preparation roadmap.
            The advisor reads your current profile, identifies strengths and gaps, and turns that into a practical plan.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Advisor Input")
    st.caption(f"Logged in as: {st.session_state.get('username', 'User')}")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    goal = st.text_input("Future Goal", placeholder="Example: AI/ML Engineer")
    extra_context = st.text_area(
        "Optional Context",
        placeholder="Add timeline, current experience, preferred tech stack, or target company type.",
        height=120,
    )
    generate_clicked = st.button("Generate AI Roadmap", use_container_width=True)


resume_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""
resume_skills = detect_resume_skills(resume_text)
goal_skills = expected_skills_for_goal(goal)
matched_skills, missing_skills = build_gap_summary(resume_skills, goal_skills)


col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.subheader("Profile Scan")
    st.write(f"Target role: `{goal or 'Not provided yet'}`")
    st.write(f"Resume extracted: `{ 'Yes' if resume_text else 'No' }`")
    st.write(f"Skills detected: `{len(resume_skills)}`")
    if resume_text:
        with st.expander("Resume Text Preview"):
            st.text(resume_text[:2500] + ("..." if len(resume_text) > 2500 else ""))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.subheader("Goal Alignment Snapshot")
    if matched_skills:
        st.markdown("**Matched skills**", unsafe_allow_html=True)
        st.markdown(
            "".join([f'<span class="chip chip-good">{skill}</span>' for skill in matched_skills]),
            unsafe_allow_html=True,
        )
    else:
        st.info("No goal-specific matched skills detected yet.")

    if missing_skills:
        st.markdown("**Skills to build next**", unsafe_allow_html=True)
        st.markdown(
            "".join([f'<span class="chip chip-gap">{skill}</span>' for skill in missing_skills]),
            unsafe_allow_html=True,
        )
    elif goal:
        st.success("No template-based skill gaps detected for this goal.")
    st.markdown("</div>", unsafe_allow_html=True)


if generate_clicked:
    if not uploaded_file:
        st.error("Please upload a resume PDF first.")
    elif not goal.strip():
        st.error("Please enter your future goal first.")
    elif not resume_text:
        st.error("I could not extract text from the uploaded PDF.")
    else:
        full_goal = goal.strip()
        if extra_context.strip():
            full_goal = f"{full_goal}. Extra context: {extra_context.strip()}"

        with st.spinner("Generating your roadmap with Gemini..."):
            roadmap_text, roadmap_error = generate_ai_roadmap(
                resume_text=resume_text,
                goal=full_goal,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
            )

        st.markdown('<div class="roadmap-box">', unsafe_allow_html=True)
        st.subheader("Detailed Career Roadmap")
        if roadmap_text:
            st.markdown(roadmap_text)
        else:
            st.info(roadmap_error or "Gemini roadmap generation failed. Showing a local roadmap instead.")
            st.markdown(generate_local_roadmap(goal.strip(), matched_skills, missing_skills))
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.write("---")
    st.markdown("### How this advisor works")
    st.write("1. Upload your resume PDF.")
    st.write("2. Enter the role you want to prepare for.")
    st.write("3. Generate a detailed roadmap based on your current profile and future goal.")
