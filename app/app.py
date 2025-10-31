import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    job_url = request.form.get('job_url')
    job_description = request.form.get('job_description', '').lower()

    if job_url:
        try:
            response = requests.get(job_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            job_description = soup.get_text(separator=' ', strip=True).lower()
        except requests.exceptions.RequestException as e:
            prediction = f"Error fetching or parsing URL: {e}"
            return render_template('index.html', prediction=prediction)

    scam_keywords = ["urgent hiring", "no experience required", "guaranteed job", "work from home", "data entry", "form filling", "limited spots", "upfront fee", "investment required"]

    if not job_description:
        prediction = "No job description or URL provided."
        return render_template('index.html', prediction=prediction)

    is_scam = any(keyword in job_description for keyword in scam_keywords)

    if is_scam:
        prediction = "This job posting has a high probability of being a scam."
    else:
        prediction = "This job posting is likely to be legitimate."

    return render_template('index.html', prediction=prediction, job_url=job_url)

import os
from PyPDF2 import PdfReader
import docx

@app.route('/upload', methods=['POST'])
def upload():
    resume = request.files.get('resume')
    suggestion = "Could not process the resume."
    if resume and resume.filename:
        try:
            filename = resume.filename
            resume_text = ""
            if filename.endswith('.pdf'):
                pdf_reader = PdfReader(resume)
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            elif filename.endswith('.docx'):
                doc = docx.Document(resume)
                for para in doc.paragraphs:
                    resume_text += para.text
            elif filename.endswith('.txt'):
                resume_text = resume.read().decode('utf-8')
            else:
                suggestion = "Unsupported file format. Please upload a .pdf, .docx, or .txt file."
                return render_template('index.html', suggestion=suggestion)

            resume_text = resume_text.lower()

            skills_courses = {
                "python": ["Advanced Python Programming", "Machine Learning with Python"],
                "java": ["Java for Enterprise Applications", "Spring Framework in Depth"],
                "javascript": ["Full-Stack Web Development with React and Node.js", "Modern JavaScript Frameworks"],
                "c++": ["Advanced C++ and Data Structures", "Game Development with C++"],
                "sql": ["Advanced SQL for Data Analysis", "Database Design and Management"]
            }

            suggested_courses = []
            for skill, courses in skills_courses.items():
                if skill in resume_text:
                    suggested_courses.extend(courses)

            if suggested_courses:
                suggestion = "Based on your resume, we suggest the following courses: " + ", ".join(suggested_courses)
            else:
                suggestion = "No specific skills detected to suggest courses. Consider adding more details to your resume."

        except Exception as e:
            suggestion = f"An error occurred while processing the resume: {e}"

    return render_template('index.html', suggestion=suggestion)

if __name__ == '__main__':
    app.run(debug=True)
