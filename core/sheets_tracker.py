import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

SHEET_URL = os.getenv("GOOGLE_SHEET_URL_OR_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

def get_sheet():
    if not os.path.exists(CREDENTIALS_FILE):
        return None
        
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        # Check if it's a URL or an ID
        if "http" in SHEET_URL:
            sheet = client.open_by_url(SHEET_URL).sheet1
        else:
            sheet = client.open_by_key(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        print(f"Error opening Google Sheet: {e}")
        return None

def log_to_sheet(company_name, email, subject, status):
    sheet = get_sheet()
    if sheet:
        try:
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [now, company_name, email, subject, status]
            sheet.append_row(row)
        except Exception as e:
            print(f"Error appending to sheet: {e}")
