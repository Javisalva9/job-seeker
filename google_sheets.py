import gspread
import datetime


def get_existing_entries(client, spreadsheet_id):
    """Returns a dictionary mapping sheet names to lists of row dictionaries"""
    existing_dict = {}
    spreadsheet = client.open_by_key(spreadsheet_id)

    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        try:
            sheet = spreadsheet.worksheet(sheet_name)
            all_values = sheet.get_all_values()
            if not all_values:
                existing_dict[sheet_name] = []
                continue
            headers = all_values[0]
            rows = []
            for row in all_values[1:]:  # Skip header row
                if len(row) >= 3 and row[1]:  # Check for Title and Company presence
                    row_dict = {
                        header: ([s.strip() for s in row[i].split(",")] if header == "Sources" and row[i] else row[i])
                        for i, header in enumerate(headers)
                        if i < len(row)
                    }
                    rows.append(row_dict)
            existing_dict[sheet_name] = rows
        except gspread.WorksheetNotFound:
            continue
    return existing_dict


def analyze_new_active(existing_entries):
    """Process New Active entries and return updated entries"""
    new_entries = existing_entries.copy()
    new_active = new_entries["New Active"].copy()

    for row in new_active:
        applied = row.get("Applied", False)
        if isinstance(applied, str):
            applied = applied.lower() == "true"

        if applied:
            new_entries["Active"].append(row)
        else:
            new_entries["Archived"].append(row)

    # Entries directly populated during processing
    new_entries["New Active"] = []
    return new_entries


def analyze_active(existing_entries):
    """Process Active entries and return updated entries"""
    new_entries = existing_entries.copy()
    active = new_entries["Active"].copy()
    new_entries["Active"] = []

    for row in active:
        try:
            added_date = datetime.datetime.fromisoformat(row.get("Added_Date", "").strip())
        except ValueError:
            added_date = datetime.datetime.min

        days_old = (datetime.datetime.now() - added_date).days
        interview_status = row.get("Interview", False)
        if isinstance(interview_status, str):
            interview_status = interview_status.lower() == "true"

        if days_old > 15 and not interview_status:
            new_entries["Archived"].append(row)
        elif interview_status:
            new_entries["Interviewing"].append(row)
        else:
            new_entries["Active"].append(row)

    # Entries directly populated during processing
    return new_entries


def analyze_archived(existing_entries):
    """Process Archived entries and return updated entries
    Logic:
    - Entries older than 30 days get permanently removed
    """
    new_entries = existing_entries.copy()
    archived = new_entries["Archived"].copy()
    new_entries["Archived"] = []

    for row in archived:
        try:
            added_date = datetime.datetime.fromisoformat(row.get("Added_Date", "").strip())
        except ValueError:
            added_date = datetime.datetime.min

        days_old = (datetime.datetime.now() - added_date).days
        if days_old > 30:
            continue
        else:
            new_entries["Archived"].append(row)

    # Entries directly populated during processing
    return new_entries


def migrate_entries(existing_entries):
    """Orchestrates the full processing workflow and returns processed data:
    1. New Active → Active/Archived based on application status
    2. Active → Archived/Interviewing based on age and interview status
    3. Archived → Permanent removal after 30 days
    4. Interviewing → Archived based on follow-up deadlines
    """
    processed_entries = analyze_new_active(existing_entries)
    processed_entries = analyze_active(processed_entries)
    processed_entries = analyze_archived(processed_entries)

    return processed_entries


def apply_entries_to_sheets(client, spreadsheet_id, processed_entries):
    """Applies in-memory entries state to Google Sheets"""
    print("📡 Syncing changes to Google Sheets...")
    spreadsheet = client.open_by_key(spreadsheet_id)

    headers = [
        "Applied",
        "Interview",
        "Title",
        "Company",
        "Score",
        "Comment",
        "Salary",
        "Locations",
        "URL",
        "Description",
        "Applicants",
        "Sources",
        "AI_Model",
        "Added_Date",
    ]

    # Update all sheets with processed entries
    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        sheet = spreadsheet.worksheet(sheet_name)
        entries = processed_entries.get(sheet_name, [])

        sheet.clear()
        if entries:
            batch_data = [headers] + [
                [
                    (
                        entry_lower.get(header.lower(), "")
                        if header.lower() != "sources"
                        else ", ".join(map(str, entry_lower.get(header.lower(), [])))
                    )
                    for header in headers
                ]
                for entry in entries
                for entry_lower in [{k.lower(): v for k, v in entry.items()}]  # Declaring entry_lower
            ]
            sheet.update(batch_data)

    print("✅ Successfully synced all sheet changes!")
