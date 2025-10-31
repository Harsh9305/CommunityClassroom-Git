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
                "python": [
                    {
                        "title": "Python for Everybody Specialization",
                        "provider": "Coursera",
                        "description": "A comprehensive introduction to Python, suitable for beginners.",
                        "url": "https://www.coursera.org/specializations/python"
                    },
                    {
                        "title": "The Complete Python Pro Bootcamp",
                        "provider": "Udemy",
                        "description": "Go from beginner to expert in Python 3. Learn to build real-world applications.",
                        "url": "https://www.udemy.com/course/100-days-of-code/"
                    }
                ],
                "java": [
                    {
                        "title": "Java Programming and Software Engineering Fundamentals",
                        "provider": "Coursera",
                        "description": "Learn to code in Java and improve your programming and software engineering skills.",
                        "url": "https://www.coursera.org/specializations/java-programming"
                    },
                    {
                        "title": "Java Programming Masterclass",
                        "provider": "Udemy",
                        "description": "A comprehensive Java course that covers everything you need to become a Java developer.",
                        "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/"
                    }
                ],
                "javascript": [
                    {
                        "title": "JavaScript for Beginners Specialization",
                        "provider": "Coursera",
                        "description": "A specialization designed to take you from a beginner to a proficient JavaScript developer.",
                        "url": "https://www.coursera.org/specializations/javascript-beginner"
                    },
                    {
                        "title": "The Complete JavaScript Course 2024: From Zero to Expert!",
                        "provider": "Udemy",
                        "description": "The modern JavaScript course for everyone! Master JavaScript with projects, challenges and theory.",
                        "url": "https://www.udemy.com/course/the-complete-javascript-course/"
                    }
                ],
                "c++": [
                    {
                        "title": "C++ For C Programmers, Part A",
                        "provider": "Coursera",
                        "description": "This course is for experienced C programmers who want to program in C++.",
                        "url": "https://www.coursera.org/learn/c-plus-plus-a"
                    },
                    {
                        "title": "Beginning C++ Programming - From Beginner to Beyond",
                        "provider": "Udemy",
                        "description": "Obtain Modern C++ Object-Oriented Programming (OOP) and STL skills.",
                        "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/"
                    }
                ],
                "sql": [
                    {
                        "title": "SQL for Data Science",
                        "provider": "Coursera",
                        "description": "Learn SQL basics, data analysis, and how to work with databases.",
                        "url": "https://www.coursera.org/learn/sql-for-data-science"
                    },
                    {
                        "title": "The Complete SQL Bootcamp: Go from Zero to Hero",
                        "provider": "Udemy",
                        "description": "Learn to use SQL quickly and effectively with this course!",
                        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"
                    }
                ]
            }

            suggested_courses = []
            for skill, courses in skills_courses.items():
                if skill in resume_text:
                    suggested_courses.extend(courses)

            if not suggested_courses:
                suggestion = "No specific skills detected to suggest courses. Consider adding more details to your resume."
                return render_template('index.html', suggestion_text=suggestion)

        except Exception as e:
            suggestion = f"An error occurred while processing the resume: {e}"
            return render_template('index.html', suggestion_text=suggestion)

    return render_template('index.html', suggested_courses=suggested_courses)

if __name__ == '__main__':
    app.run(debug=True)
