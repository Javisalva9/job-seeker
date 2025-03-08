import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def save_to_google_sheets(jobs, spreadsheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(spreadsheet_id).sheet1  # Use the first sheet

    # Clear existing content before writing new data
    sheet.clear()

    # Add headers
    headers = ["Title", "Company", "Description", "Applicants", "Locations", "Salary Range", "URL", "Match Rating", "Match Comment", "Sources", "AI Model"]
    sheet.append_row(headers)

    # 🛠 **Fix: Batch Writing Instead of One-by-One** 🛠
    rows = []
    for job in jobs:
        row = [
            job.get("title", ""),
            job.get("company", ""),
            job.get("description", ""),
            job.get("applicants", ""),
            job.get("locations", ""),
            job.get("salary_range", ""),
            job.get("url", ""),
            job.get("match_rating", ""),
            job.get("match_comment", ""),
            str(job.get("sources", "")),
            job.get("ai_model", ""),
        ]
        rows.append(row)

    if rows:
        sheet.append_rows(rows)  # ✅ This writes all rows at once (avoiding rate limits)

    print("✅ Data successfully written to Google Sheets!")
