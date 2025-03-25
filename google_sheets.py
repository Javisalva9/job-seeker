import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import time


def get_existing_entries(client, spreadsheet_id):
    """Returns set of (title, company) tuples from all sheets"""
    existing = set()
    spreadsheet = client.open_by_key(spreadsheet_id)

    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
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

    print("🔄 Starting migration process...")
    spreadsheet = client.open_by_key(spreadsheet_id)

    headers = [
        "Applied",
        "Interview",
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
        "Recover",
    ]

    # Ensure all sheets have correct headers
    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        sheet = spreadsheet.worksheet(sheet_name)
        current_headers = sheet.row_values(1)
        if current_headers != headers:
            all_data = sheet.get_all_values()
            new_data = [headers] + (all_data[1:] if len(all_data) > 1 else [])
            sheet.clear()
            if new_data:
                sheet.update(new_data)

    # Migration rules
    active_sheet = spreadsheet.worksheet("Active")
    archived_sheet = spreadsheet.worksheet("Archived")
    interviewing_sheet = spreadsheet.worksheet("Interviewing")

    # Migrate stale active entries to archived
    # Process New Active -> Active/Archived
    new_active_sheet = spreadsheet.worksheet("New Active")
    new_active_rows = new_active_sheet.get_all_records(expected_headers=headers)

    # Batch process New Active entries
    active_batch = []
    archived_batch = []

    for row in reversed(new_active_rows):
        # Convert string 'False'/'True' to boolean if needed
        applied = row.get("Applied", False)
        if isinstance(applied, str):
            applied = applied.lower() == "true"

        if applied:
            print(f"Moving to Active: {row.get('Title', 'Unknown')} at {row.get('Company', 'Unknown')}")
            active_batch.append(list(row.values()))
        else:
            print(f"Moving to Archived: {row.get('Title', 'Unknown')} at {row.get('Company', 'Unknown')}")
            archived_batch.append(list(row.values()))

    if active_batch:
        active_sheet.append_rows(active_batch)
    if archived_batch:
        archived_sheet.append_rows(archived_batch)

    # Only delete rows if there are rows to delete
    if new_active_rows and new_active_sheet.row_count > 1:
        new_active_sheet.delete_rows(2, new_active_sheet.row_count - 1)

    # Batch process Active entries
    active_rows = active_sheet.get_all_records(expected_headers=headers)
    archive_candidates = []
    interview_candidates = []

    print(f"Processing {len(active_rows)} entries in Active sheet")
    for row in reversed(active_rows):
        try:
            added_date = datetime.datetime.fromisoformat(row.get("Added Date", "").strip())
        except ValueError:
            added_date = datetime.datetime.min

        days_old = (datetime.datetime.now() - added_date).days
        interview_status = row.get("Interview", False)

        # Convert string 'False'/'True' to boolean if needed
        if isinstance(interview_status, str):
            interview_status = interview_status.lower() == "true"

        # Debug output
        job_title = row.get("Title", "Unknown")
        job_company = row.get("Company", "Unknown")

        if days_old > 15 and not interview_status:
            print(f"Moving to Archived (age: {days_old} days): {job_title} at {job_company}")
            archive_candidates.append(list(row.values()))
        elif interview_status:
            print(f"Moving to Interviewing: {job_title} at {job_company}")
            interview_candidates.append(list(row.values()))
        else:
            print(f"Keeping in Active: {job_title} at {job_company}")

    if archive_candidates:
        print(f"Adding {len(archive_candidates)} entries to Archived sheet")
        archived_sheet.append_rows(archive_candidates)
    if interview_candidates:
        print(f"Adding {len(interview_candidates)} entries to Interviewing sheet")
        interviewing_sheet.append_rows(interview_candidates)

    # Only delete rows if there are rows to delete and we've moved them
    rows_to_delete = len(archive_candidates) + len(interview_candidates)
    if rows_to_delete > 0 and active_sheet.row_count > 1:
        active_sheet.delete_rows(2, min(rows_to_delete, active_sheet.row_count - 1))

    # We no longer need this section as we already handle moving entries to interviewing
    # based on the Interview flag above. This was causing duplicate entries.

    # Migrate old interviewing entries to archived
    headers = [
        "Applied",
        "Interview",
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
        "Recover",
    ]
    active_rows = active_sheet.get_all_records(expected_headers=headers)
    interviewing_rows = interviewing_sheet.get_all_records(expected_headers=headers)
    # Batch process interviewing entries
    archive_candidates = []
    for row in reversed(interviewing_rows):
        try:
            added_date_str = row.get("Added Date", "").strip()
            added_date = datetime.datetime.fromisoformat(added_date_str) if added_date_str else datetime.datetime.min
        except ValueError:
            added_date = datetime.datetime.min

        if (datetime.datetime.now() - added_date).days > 60:
            archive_candidates.append(list(row.values()))

    if archive_candidates and interviewing_rows:
        archived_sheet.append_rows(archive_candidates)
        # Make sure we don't try to delete more rows than exist
        if len(interviewing_rows) > 0:
            interviewing_sheet.delete_rows(2, min(len(archive_candidates), interviewing_sheet.row_count - 1))

    # Process Archived recover entries
    archived_rows = archived_sheet.get_all_records(expected_headers=headers)
    # Batch process Archived recover entries
    recover_batch = [list(row.values()) for row in reversed(archived_rows) if row.get("Recover", False)]

    if recover_batch and archived_rows:
        active_sheet.append_rows(recover_batch)
        # Make sure we don't try to delete more rows than exist
        if len(archived_rows) > 0:
            archived_sheet.delete_rows(2, min(len(recover_batch), archived_sheet.row_count - 1))

    # Sort all sheets by Score before rewriting
    def sort_and_rewrite(sheet):
        records = sheet.get_all_records(expected_headers=headers)

        # Safe conversion of Score to float with error handling
        def safe_score(record):
            try:
                score = record.get("Score", "0")
                return float(score) if score else 0
            except (ValueError, TypeError):
                return 0

        sorted_records = sorted(records, key=safe_score, reverse=True)

        # Only clear and update if we have records to write
        if sorted_records:
            sheet.clear()
            sheet.update([headers] + [list(r.values()) for r in sorted_records])

    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        sheet = spreadsheet.worksheet(sheet_name)
        sort_and_rewrite(sheet)
        time.sleep(3)


def save_to_google_sheets(jobs, spreadsheet_id):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
    client = gspread.authorize(creds)

    # Create sheets if missing
    spreadsheet = client.open_by_key(spreadsheet_id)
    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        try:
            spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)

    # Initialize New Active sheet reference - we always add new jobs to New Active
    sheet = spreadsheet.worksheet("New Active")

    # Get existing entries to prevent duplication
    existing_entries = get_existing_entries(client, spreadsheet_id)
    new_jobs = [job for job in jobs if (job.get("title"), job.get("company")) not in existing_entries]

    # Ensure all sheets have headers
    headers = [
        "Applied",
        "Interview",
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
        "Recover",
    ]

    # Check if sheet is empty and add headers if needed
    is_sheet_empty = not sheet.get_all_values() or sheet.get_all_values() == [[]]
    if is_sheet_empty:
        sheet.append_row(headers)

    rows = []
    for job in new_jobs:
        # Ensure applied and interview are proper boolean values
        # Use lowercase 'applied' key first, then try capitalized 'Applied' as fallback
        applied = job.get("applied", job.get("Applied", False))
        if isinstance(applied, str):
            applied = applied.lower() == "true"

        interview = job.get("interview", False)
        if isinstance(interview, str):
            interview = interview.lower() == "true"

        # Debug output
        print(f"Adding new job: {job.get('title')} at {job.get('company')}")
        print(f"  Applied: {applied}, Interview: {interview}")

        row = [
            applied,
            interview,  # Add Interview field as second column
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
            False,  # Recover field
        ]
        rows.append(row)

    if rows:
        # Simply append new rows to New Active sheet
        sheet.append_rows(rows)

        try:
            # Run migration after saving new entries
            migrate_entries(client, spreadsheet_id)

            print("✅ Data successfully written to Google Sheets!")
        except gspread.exceptions.APIError as e:
            if "quota" in str(e).lower():
                print("⚠️  Critical: API Quota exhausted. Please check:")
                print(
                    """1. Google Cloud Console quotas:
                     https://console.cloud.google.com/apis/api/sheets.googleapis.com/quotas"""
                )
                print("2. Wait 1-2 minutes before retrying")
                raise SystemExit(1)
