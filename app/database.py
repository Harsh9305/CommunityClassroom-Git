import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create table for job scans
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            prediction TEXT NOT NULL,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create table for resume scans
    c.execute('''
        CREATE TABLE IF NOT EXISTS resume_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            skills TEXT,
            job_role_id INTEGER,
            match_percentage REAL,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_role_id) REFERENCES job_roles(id)
        )
    ''')

    # Create table for skills
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create table for job roles
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create table for job role skills mapping
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_role_skills (
            job_role_id INTEGER,
            skill_id INTEGER,
            PRIMARY KEY (job_role_id, skill_id),
            FOREIGN KEY (job_role_id) REFERENCES job_roles(id),
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        )
    ''')

    # Pre-populate skills
    skills = ['Python', 'Java', 'JavaScript', 'C++', 'SQL', 'React', 'Node.js', 'TensorFlow', 'PyTorch', 'AWS']
    for skill in skills:
        c.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))

    # Pre-populate job roles
    job_roles = ['Data Scientist', 'Software Engineer', 'Web Developer']
    for role in job_roles:
        c.execute("INSERT OR IGNORE INTO job_roles (name) VALUES (?)", (role,))

    # Pre-populate job role skills mapping
    job_role_skills = {
        'Data Scientist': ['Python', 'SQL', 'TensorFlow', 'PyTorch'],
        'Software Engineer': ['Python', 'Java', 'C++', 'AWS'],
        'Web Developer': ['JavaScript', 'React', 'Node.js', 'SQL']
    }
    for role, skills in job_role_skills.items():
        role_id = c.execute("SELECT id FROM job_roles WHERE name = ?", (role,)).fetchone()[0]
        for skill in skills:
            skill_id = c.execute("SELECT id FROM skills WHERE name = ?", (skill,)).fetchone()[0]
            c.execute("INSERT OR IGNORE INTO job_role_skills (job_role_id, skill_id) VALUES (?, ?)", (role_id, skill_id))

    conn.commit()
    conn.close()
