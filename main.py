from config.user_config import load_user_config
import os
from job_scraper import scrape_all
from google_sheets import get_existing_entries, migrate_entries, apply_entries_to_sheets
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from openrouter import evaluate_all_jobs


def set_test_mode():
    import sys

    if "--test" in sys.argv:
        os.environ["TEST_MODE"] = "1"
        print("🔧 Test mode enabled")


def main():
    print("🚀 Starting job search process!")
    set_test_mode()
    user = load_user_config()
    scraped_jobs = scrape_all(user)
    # Check existing entries before AI processing
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
    client = gspread.authorize(creds)

    # Create sheets if missing
    spreadsheet = client.open_by_key(user.spreadsheet_id)
    for sheet_name in ["New Active", "Active", "Archived", "Interviewing"]:
        try:
            spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)

    existing_entries = get_existing_entries(client, user.spreadsheet_id)
    existing_titles_companies = set()
    for sheet_entries in existing_entries.values():
        for entry in sheet_entries:
            title = entry.get("Title", "")
            company = entry.get("Company", "")
            if title and company:
                existing_titles_companies.add((title, company))
    new_jobs = [
        job for job in scraped_jobs if (job.get("title", ""), job.get("company", "")) not in existing_titles_companies
    ]

    print("🧠 Starting AI review process now...")
    evaluated_jobs = evaluate_all_jobs(user, new_jobs)

    processed_entries = migrate_entries(existing_entries)

    processed_entries["New Active"] = evaluated_jobs

    # Apply processed entries to sheets
    print("📊 Saving processed entries to Google Sheets!")
    apply_entries_to_sheets(client, user.spreadsheet_id, processed_entries)
    print("🎉 All done!")


if __name__ == "__main__":
    main()
