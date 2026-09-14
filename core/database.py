import sqlite3
import datetime
import os

DB_NAME = "db.sqlite3"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for resources (IA agency resources, agents, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Table for the email queue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_query TEXT,
            company_name TEXT,
            website TEXT,
            email TEXT,
            context TEXT,
            email_subject TEXT,
            email_body TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME,
            sent_at DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

# --- Resource Management ---

def add_resource(name, url, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resources (name, url, description, is_active)
        VALUES (?, ?, ?, 1)
    ''', (name, url, description))
    conn.commit()
    conn.close()

def get_all_resources():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resources')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "url": r[2], "description": r[3], "is_active": bool(r[4])} for r in rows]

def get_active_resources():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resources WHERE is_active = 1')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "url": r[2], "description": r[3], "is_active": bool(r[4])} for r in rows]

def toggle_resource(resource_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE resources SET is_active = ? WHERE id = ?', (1 if is_active else 0, resource_id))
    conn.commit()
    conn.close()
    
def delete_resource(resource_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM resources WHERE id = ?', (resource_id,))
    conn.commit()
    conn.close()

# --- Email Queue Management ---

def add_to_queue(search_query, company_name, website, email, context, email_subject, email_body):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO email_queue (search_query, company_name, website, email, context, email_subject, email_body, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (search_query, company_name, website, email, context, email_subject, email_body, now))
    conn.commit()
    conn.close()

def get_pending_emails(limit=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM email_queue WHERE status = "pending" ORDER BY created_at ASC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "search_query": r[1],
            "company_name": r[2],
            "website": r[3],
            "email": r[4],
            "context": r[5],
            "email_subject": r[6],
            "email_body": r[7],
            "status": r[8],
            "created_at": r[9],
            "sent_at": r[10]
        })
    return result

def mark_email_sent(email_id):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute('UPDATE email_queue SET status = "sent", sent_at = ? WHERE id = ?', (now, email_id))
    conn.commit()
    conn.close()

def mark_email_failed(email_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE email_queue SET status = "failed" WHERE id = ?', (email_id,))
    conn.commit()
    conn.close()
    
def get_queue_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status, COUNT(*) FROM email_queue GROUP BY status')
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}
