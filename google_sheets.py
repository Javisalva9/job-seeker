import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime


def get_existing_entries(client, spreadsheet_id):
    """Returns set of (title, company) tuples from all sheets"""
    existing = set()
    spreadsheet = client.open_by_key(spreadsheet_id)

    for sheet_name in ["Active", "Archived", "Interviewing"]:
        try:
            sheet = spreadsheet.worksheet(sheet_name)
            all_values = sheet.get_all_values()
            for row in all_values:
                if len(row) >= 3 and row[1]:  # Title (B) and Company (C)
                    existing.add((row[1], row[2]))
        except gspread.WorksheetNotFound:
            continue
    return existing


def migrate_entries(client, spreadsheet_id):
    """Moves entries between sheets based on status and time thresholds"""
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Migration rules
    active_sheet = spreadsheet.worksheet("Active")
    archived_sheet = spreadsheet.worksheet("Archived")
    interviewing_sheet = spreadsheet.worksheet("Interviewing")

    # Migrate stale active entries to archived
    active_rows = active_sheet.get_all_records()
    for i, row in enumerate(reversed(active_rows), 1):
        added_date = datetime.datetime.fromisoformat(row.get("Added Date", ""))
        if (datetime.datetime.now() - added_date).days > 30 and not row.get("Applied", False):
            archived_sheet.append_row(list(row.values()))
            active_sheet.delete_rows(active_sheet.row_count - i + 1)

    # Migrate applied entries to interviewing
    for i, row in enumerate(reversed(active_rows), 1):
        if row.get("Applied", False):
            interviewing_sheet.append_row(list(row.values()))
            active_sheet.delete_rows(active_sheet.row_count - i + 1)

    # Migrate old interviewing entries to archived
    interviewing_rows = interviewing_sheet.get_all_records()
    for i, row in enumerate(reversed(interviewing_rows), 1):
        added_date = datetime.datetime.fromisoformat(row.get("Added Date", ""))
        if (datetime.datetime.now() - added_date).days > 60:
            archived_sheet.append_row(list(row.values()))
            interviewing_sheet.delete_rows(interviewing_sheet.row_count - i + 1)


def save_to_google_sheets(jobs, spreadsheet_id):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
    client = gspread.authorize(creds)

    # Create sheets if missing
    spreadsheet = client.open_by_key(spreadsheet_id)
    for sheet_name in ["Active", "Archived", "Interviewing"]:
        try:
            spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)

    # Initialize active sheet reference
    sheet = spreadsheet.worksheet("Active")

    existing_entries = get_existing_entries(client, spreadsheet_id)
    new_jobs = [job for job in jobs if (job.get("title"), job.get("company")) not in existing_entries]

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
            "Added Date",
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
            datetime.datetime.now().isoformat(),
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

    # Run migration after saving new entries
    migrate_entries(client, spreadsheet_id)

    print("✅ Data successfully written to Google Sheets!")
