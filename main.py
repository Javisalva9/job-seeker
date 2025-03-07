from config import Miguel, Javi
import argparse
from job_scraper import find_all  # dynamically loads scrapers and merges duplicates
from google_sheets import save_to_google_sheets
from openrouter import evaluate_all_jobs  # adds match_rating and match_comment to jobs

def get_user():
    parser = argparse.ArgumentParser(description="Select a user for scraping.")
    parser.add_argument("--miguel", action="store_true", help="Run the script for Miguel")
    parser.add_argument("--javi", action="store_true", help="Run the script for Javi")
    args = parser.parse_args()
    if args.miguel:
        return Miguel
    elif args.javi:
        return Javi
    else:
        parser.error("❌ You must specify --miguel or --javi")

def main():
    user = get_user()
    all_jobs = find_all(user)
    evaluated_jobs = evaluate_all_jobs(user, all_jobs)
    save_to_google_sheets(evaluated_jobs, user.spreadsheet_id)

if __name__ == "__main__":
    main()
