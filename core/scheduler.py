import time
from apscheduler.schedulers.background import BackgroundScheduler
from core.database import get_pending_emails, mark_email_sent, mark_email_failed
from core.mailer import send_email
from core.sheets_tracker import log_to_sheet

def process_email_queue():
    pending = get_pending_emails(limit=1)
    if not pending:
        return
        
    email_data = pending[0]
    email_id = email_data['id']
    to_email = email_data['email']
    subject = email_data['email_subject']
    body = email_data['email_body']
    company_name = email_data['company_name']
    
    # Check if there is an email
    if not to_email:
        mark_email_failed(email_id)
        log_to_sheet(company_name, "NO_EMAIL", "N/A", "Failed (No Email)")
        return
        
    try:
        print(f"Sending email to {to_email}...")
        send_email(to_email, subject, body)
        mark_email_sent(email_id)
        log_to_sheet(company_name, to_email, subject, "Sent")
        print("Success!")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        mark_email_failed(email_id)
        log_to_sheet(company_name, to_email, subject, f"Failed: {str(e)}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Execute the queue processor every 5 minutes
    scheduler.add_job(process_email_queue, 'interval', minutes=5)
    scheduler.start()
    return scheduler
