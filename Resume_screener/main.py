import re
import os
from pdfminer.high_level import extract_text

# job description
job_desc = """
We are looking for a Python developer with skills in data analysis,
machine learning, and problem solving.
"""

# clean job description
job_desc = job_desc.lower()
job_desc = re.sub(r'[^a-zA-Z0-9\s]', ' ', job_desc)
job_desc = re.sub(r'\s+', ' ', job_desc)

# stopwords
stopwords = {
    "and", "the", "is", "with", "a", "we", "are",
    "for", "in", "to", "of", "on", "this", "that"
}

job_words = set(job_desc.split()) - stopwords

# important skills
important_skills = {"python", "data analysis", "machine learning", "problem solving"}

# folder path
folder_path = r'C:\Users\karan\OneDrive\Desktop\Resume'

results = []

for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)

        # extract text
        text = extract_text(file_path)

        # clean text
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # word processing
        resume_words = set(text.split()) - stopwords
        matching_words = resume_words.intersection(job_words)

        score = len(matching_words) / len(job_words) * 100

        # skill check
        missing_skills = []
        for skill in important_skills:
            if skill not in text:
                missing_skills.append(skill)

        # store result
        results.append((filename, score, missing_skills))

# sort results AFTER loop
results.sort(key=lambda x: x[1], reverse=True)

# print results
for r in results:
    print("Resume:", r[0])
    print("Score:", f"{r[1]:.2f}%")
    print("Missing Skills:", r[2])
    print("-" * 40)