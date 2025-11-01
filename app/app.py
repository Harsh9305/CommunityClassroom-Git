import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import database

app = Flask(__name__)

# Initialize the database
database.init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    # Get metrics
    total_scans = conn.execute('SELECT COUNT(*) FROM job_scans').fetchone()[0]
    untrustworthy_scans = conn.execute('SELECT COUNT(*) FROM job_scans WHERE prediction = ?',
                                       ("This job posting has a high probability of being a scam.",)).fetchone()[0]
    trustworthy_scans = total_scans - untrustworthy_scans

    # Get recent job scans
    job_scans = conn.execute('SELECT * FROM job_scans ORDER BY scan_date DESC LIMIT 5').fetchall()

    # Get recent resume scans
    resume_scans = conn.execute('SELECT * FROM resume_scans ORDER BY scan_date DESC LIMIT 5').fetchall()

    conn.close()

    return render_template('dashboard.html',
                           total_scans=total_scans,
                           untrustworthy_scans=untrustworthy_scans,
                           trustworthy_scans=trustworthy_scans,
                           job_scans=job_scans,
                           resume_scans=resume_scans)

@app.route('/scan')
def scan():
    conn = get_db_connection()
    job_roles = conn.execute('SELECT * FROM job_roles').fetchall()
    conn.close()
    error = request.args.get('error')
    return render_template('scan.html', job_roles=job_roles, error=error)

@app.route('/resume_result/<int:scan_id>')
def resume_result(scan_id):
    conn = get_db_connection()
    scan = conn.execute('SELECT * FROM resume_scans WHERE id = ?', (scan_id,)).fetchone()
    job_role_id = scan['job_role_id']
    job_role = conn.execute('SELECT name FROM job_roles WHERE id = ?', (job_role_id,)).fetchone()['name']

    required_skills_rows = conn.execute('''
        SELECT s.name FROM skills s
        JOIN job_role_skills jrs ON s.id = jrs.skill_id
        WHERE jrs.job_role_id = ?
    ''', (job_role_id,)).fetchall()
    required_skills = [row['name'] for row in required_skills_rows]

    extracted_skills = scan['skills'].split(',')

    match_count = len(set(required_skills) & set(extracted_skills))
    match_percentage = (match_count / len(required_skills)) * 100 if required_skills else 0

    # Update the database with the match percentage
    conn.execute('UPDATE resume_scans SET match_percentage = ? WHERE id = ?', (match_percentage, scan_id))
    conn.commit()

    skills_courses = {
        "python": [
            {"title": "Python for Everybody Specialization", "provider": "Coursera", "description": "A comprehensive introduction to Python, suitable for beginners.", "url": "https://www.coursera.org/specializations/python"},
            {"title": "The Complete Python Pro Bootcamp", "provider": "Udemy", "description": "Go from beginner to expert in Python 3. Learn to build real-world applications.", "url": "https://www.udemy.com/course/100-days-of-code/"}
        ],
        "java": [
            {"title": "Java Programming and Software Engineering Fundamentals", "provider": "Coursera", "description": "Learn to code in Java and improve your programming and software engineering skills.", "url": "https://www.coursera.org/specializations/java-programming"},
            {"title": "Java Programming Masterclass", "provider": "Udemy", "description": "A comprehensive Java course that covers everything you need to become a Java developer.", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/"}
        ],
        "javascript": [
            {"title": "JavaScript for Beginners Specialization", "provider": "Coursera", "description": "A specialization designed to take you from a beginner to a proficient JavaScript developer.", "url": "https://www.coursera.org/specializations/javascript-beginner"},
            {"title": "The Complete JavaScript Course 2024: From Zero to Expert!", "provider": "Udemy", "description": "The modern JavaScript course for everyone! Master JavaScript with projects, challenges and theory.", "url": "https://www.udemy.com/course/the-complete-javascript-course/"}
        ],
        "c++": [
            {"title": "C++ For C Programmers, Part A", "provider": "Coursera", "description": "This course is for experienced C programmers who want to program in C++.", "url": "https://www.coursera.org/learn/c-plus-plus-a"},
            {"title": "Beginning C++ Programming - From Beginner to Beyond", "provider": "Udemy", "description": "Obtain Modern C++ Object-Oriented Programming (OOP) and STL skills.", "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/"}
        ],
        "sql": [
            {"title": "SQL for Data Science", "provider": "Coursera", "description": "Learn SQL basics, data analysis, and how to work with databases.", "url": "https://www.coursera.org/learn/sql-for-data-science"},
            {"title": "The Complete SQL Bootcamp: Go from Zero to Hero", "provider": "Udemy", "description": "Learn to use SQL quickly and effectively with this course!", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"}
        ]
    }

    suggested_courses = []
    for skill in extracted_skills:
        if skill.lower() in skills_courses:
            suggested_courses.extend(skills_courses[skill.lower()])

    conn.close()

    return render_template('resume_result.html',
                           scan=scan,
                           job_role=job_role,
                           required_skills=required_skills,
                           extracted_skills=extracted_skills,
                           match_percentage=match_percentage,
                           suggested_courses=suggested_courses)

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
            return redirect(url_for('scan', error=f"Error fetching or parsing URL: {e}"))

    scam_keywords = ["urgent hiring", "no experience required", "guaranteed job", "work from home", "data entry", "form filling", "limited spots", "upfront fee", "investment required"]

    if not job_description:
        return redirect(url_for('scan', error="No job description or URL provided."))

    is_scam = any(keyword in job_description for keyword in scam_keywords)

    if is_scam:
        prediction = "This job posting has a high probability of being a scam."
    else:
        prediction = "This job posting is likely to be legitimate."

    # Save the scan to the database
    conn = get_db_connection()
    conn.execute('INSERT INTO job_scans (content, prediction) VALUES (?, ?)',
                 (job_description, prediction))
    conn.commit()
    conn.close()

    return render_template('index.html', prediction=prediction, job_url=job_url)

import os
from PyPDF2 import PdfReader
import docx

@app.route('/upload', methods=['POST'])
def upload():
    resume = request.files.get('resume')
    job_role_id = request.form.get('job_role')
    suggestion = "Could not process the resume."
    if resume and resume.filename and job_role_id:
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
                return redirect(url_for('scan', error="Unsupported file format. Please upload a .pdf, .docx, or .txt file."))

            resume_text = resume_text.lower()

            conn = get_db_connection()
            skills_from_db = conn.execute('SELECT name FROM skills').fetchall()

            extracted_skills = []
            for skill in skills_from_db:
                if skill['name'].lower() in resume_text:
                    extracted_skills.append(skill['name'])

            if not extracted_skills:
                conn.close()
                return redirect(url_for('scan', error="No specific skills detected to suggest courses. Consider adding more details to your resume."))

            # For now, we'll just save the skills. The full analysis will be on a separate page.
            conn.execute('INSERT INTO resume_scans (filename, skills, job_role_id) VALUES (?, ?, ?)',
                         (filename, ','.join(extracted_skills), job_role_id))
            conn.commit()
            scan_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.close()

            # Redirect to a new page for detailed analysis
            return redirect(url_for('resume_result', scan_id=scan_id))

        except Exception as e:
            suggestion = f"An error occurred while processing the resume: {e}"
            return render_template('index.html', suggestion_text=suggestion)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
