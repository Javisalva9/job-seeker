from config import Miguel, Javi
import argparse
import os
from job_scraper import find_all
from google_sheets import save_to_google_sheets, get_existing_entries
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from openrouter import evaluate_all_jobs


def get_user():
    parser = argparse.ArgumentParser(description="Select a user for scraping.")
    parser.add_argument("--miguel", action="store_true", help="Run the script for Miguel")
    parser.add_argument("--javi", action="store_true", help="Run the script for Javi")
    args, _ = parser.parse_known_args()  # Unpack tuple correctly

    if args.miguel:
        return Miguel
    elif args.javi:
        return Javi
    else:
        parser.error("❌ You must specify --miguel or --javi")


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
    user = get_user()
    all_jobs = find_all(user)
    # Check existing entries before AI processing
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
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
