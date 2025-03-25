from config.user_config import load_user_config
import os
from job_scraper import find_all
from google_sheets import save_to_google_sheets, get_existing_entries
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
    all_jobs = find_all(user)
    # Check existing entries before AI processing
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
    client = gspread.authorize(creds)
    existing_entries = get_existing_entries(client, user.spreadsheet_id)
    new_jobs = [job for job in all_jobs if (job.get("title"), job.get("company")) not in existing_entries]

    # Convert interview_status field to interview boolean field
    for job in new_jobs:
        # Check if job has interview_status field and convert it to interview boolean
        if "interview_status" in job:
            # Only set interview to True if status is not 'pending'
            job["interview"] = job["interview_status"].lower() != "pending"

    print("🧠 Starting AI review process now...")
    evaluated_jobs = evaluate_all_jobs(user, new_jobs)
    print("📊 Saving results to Google Sheets!")
    save_to_google_sheets(evaluated_jobs, user.spreadsheet_id)
    # migrate_entries is now called from within save_to_google_sheets
    print("🎉 All done!")


if __name__ == "__main__":
    main()
