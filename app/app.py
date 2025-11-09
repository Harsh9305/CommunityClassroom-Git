from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
import sqlite3
import database
import os
from PyPDF2 import PdfReader
import docx
# from googlesearch import search as google_search_lib # Commented out due to unreliability

app = Flask(__name__)

# --- Database Setup ---
database.init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Main UI Route ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Feature: Real-time Company Verification ---
@app.route('/verify-company', methods=['POST'])
def verify_company():
    company_name = request.json.get('company_name', '')
    if not company_name:
        return jsonify({'status': 'error', 'message': 'Company name is required.'}), 400

    # --- MOCK IMPLEMENTATION ---
    # The 'googlesearch' library is unofficial and frequently blocked by Google,
    # making it too unreliable for a stable application. A production implementation
    # would require a paid, official search API (e.g., Google Custom Search API, SerpAPI).
    # This mock simulates the behavior of such an API for demonstration and testing.

    if company_name.lower() == 'google':
        message = "'Google' appears to be a legitimate company."
        details = [
            "Found official website: https://www.google.com",
            "Found LinkedIn Profile: https://www.linkedin.com/company/google",
            "Positive reviews found on Glassdoor."
        ]
    else:
        message = f"Could not determine the legitimacy of '{company_name}'. Please do your own research."
        details = ["No significant information found. This could be a new company or a red flag."]

    return jsonify({'status': 'success', 'message': message, 'details': details})


# --- Feature: Job Scam Prediction ---
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
            return render_template('index.html', prediction_error=f"Error fetching or parsing URL: {e}")

    scam_keywords = ["urgent hiring", "no experience required", "guaranteed job", "work from home", "data entry", "form filling", "limited spots", "upfront fee", "investment required"]

    if not job_description:
        return render_template('index.html', prediction_error="No job description or URL provided.")

    is_scam = any(keyword in job_description for keyword in scam_keywords)

    prediction = "This job posting has a high probability of being a scam." if is_scam else "This job posting is likely to be legitimate."

    conn = get_db_connection()
    conn.execute('INSERT INTO job_scans (content, prediction) VALUES (?, ?)',
                 (job_description[:5000], prediction))
    conn.commit()
    conn.close()

    return render_template('index.html', prediction_result=prediction, job_url=job_url)

# --- Feature: Resume Analysis ---
@app.route('/upload', methods=['POST'])
def upload():
    resume = request.files.get('resume')
    job_role_id = request.form.get('job_role')

    if not resume or not resume.filename:
        return render_template('index.html', resume_error="No resume file provided.")

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
            return render_template('index.html', resume_error="Unsupported file format. Please upload a .pdf, .docx, or .txt file.")

        resume_text = resume_text.lower()

        conn = get_db_connection()
        skills_from_db = conn.execute('SELECT name FROM skills').fetchall()

        extracted_skills = [skill['name'] for skill in skills_from_db if skill['name'].lower() in resume_text]

        if not extracted_skills:
            conn.close()
            return render_template('index.html', resume_error="No specific skills detected from your resume.")

        conn.execute('INSERT INTO resume_scans (filename, skills, job_role_id) VALUES (?, ?, ?)',
                     (filename, ','.join(extracted_flags), job_role_id))
        conn.commit()
        conn.close()

        return render_template('index.html', resume_success=f"Successfully analyzed '{filename}'. Found skills: {', '.join(extracted_skills)}")

    except Exception as e:
        return render_template('index.html', resume_error=f"An error occurred: {e}")

if __name__ == '__main__':
    app.run(debug=True)
