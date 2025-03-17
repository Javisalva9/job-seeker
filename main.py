from config.user_config import load_user_config
import argparse
import os
from job_scraper import find_all
from google_sheets import save_to_google_sheets, get_existing_entries
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from openrouter import evaluate_all_jobs


def set_test_mode():
    parser = argparse.ArgumentParser(description="Enable test mode")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args, _ = parser.parse_known_args()  # Unpack tuple correctly

    if args.test:
        # Store test mode as an environment variable
        os.environ["TEST_MODE"] = "1"


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
    sheet = client.open_by_key(user.spreadsheet_id).sheet1
    existing_entries = get_existing_entries(sheet)
    new_jobs = [job for job in all_jobs if (job.get("title"), job.get("company")) not in existing_entries]
    print("🧠 Starting AI review process now...")
    evaluated_jobs = evaluate_all_jobs(user, new_jobs)
    print("📊 Saving results to Google Sheets!")
    save_to_google_sheets(evaluated_jobs, user.spreadsheet_id)
    print("🎉 All done!")


if __name__ == "__main__":
    main()
