import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_existing_entries(sheet):
    """Returns set of (title, company) tuples and first empty row index"""
    all_values = sheet.get_all_values()
    existing = set()

    for i, row in enumerate(all_values):
        if len(row) >= 2 and row[1]:  # Check Title column (B)
            existing.add((row[1], row[2]))  # Title (B) and Company (C)

    return existing


def save_to_google_sheets(jobs, spreadsheet_id):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).sheet1  # Use the first sheet

    # Get existing entries and filter new jobs
    existing_entries = get_existing_entries(sheet)
    new_jobs = [j for j in jobs if (j.get("title"), j.get("company")) not in existing_entries]

    # Only add headers if sheet is empty
    is_sheet_empty = not sheet.get_all_values() or sheet.get_all_values() == [[]]
    if is_sheet_empty:
        headers = [
            "Applied",
            "Title",
            "Company",
            "Score",
            "AI Comments",
            "Salary Range",
            "Locations",
            "URL",
            "Description",
            "Applicants",
            "Sources",
            "AI Model",
        ]
        sheet.append_row(headers)

    rows = []
    for job in new_jobs:
        row = [
            job.get("applied", False),
            job.get("title", ""),
            job.get("company", ""),
            job.get("score", ""),
            job.get("comment", ""),
            job.get("salary_range", ""),
            job.get("locations", ""),
            job.get("url", ""),
            job.get("description", ""),
            job.get("applicants", ""),
            ", ".join(job.get("sources", [])),
            job.get("ai_model", ""),
        ]
        rows.append(row)

    if rows:
        # Find first empty row in column B
        all_values = sheet.get_all_values()
        first_empty_row = len(all_values) + 1  # Fallback to append

        for i, row in enumerate(all_values, start=1):
            if len(row) < 2 or not row[1]:  # Check if Title (B) is empty
                first_empty_row = i
                break

        # Update empty row if found, else append
        sheet.update(f"A{first_empty_row}", rows)

    print("✅ Data successfully written to Google Sheets!")
