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
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
