import os
from dotenv import load_dotenv
from openrouter import ask_openrouter

# Load .env file
load_dotenv()

# Test if the API key is loaded correctly
if not os.getenv("OPENROUTER_API_KEY"):
    raise ValueError("❌ Missing OpenRouter API key! Set it in a .env file.")

# Test OpenRouter API
response = ask_openrouter("Do you believe you can compare my cv and goals to job offers and make a point system so I can sort it on a sheet ?")
print(response)
""" 
import json
import time
import argparse
from playwright.sync_api import sync_playwright
from config import Miguel, Javi
from google_sheets import save_to_google_sheets  # Google Sheets integration

# Parse command-line arguments
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

def scrape_job_details(page):
    job_info = {}

    # Title
    title_el = page.query_selector("h1.job-title")
    job_info["title"] = title_el.inner_text().strip() if title_el else None

    # Company
    company_el = page.query_selector("div.job-company span a")
    job_info["company"] = company_el.inner_text().strip() if company_el else None

    # 🛠 Fix: Extract Description Without Title & Company 🛠
    job_el = page.query_selector("div.job")
    desc_elements = job_el.query_selector_all("p, ul, li")  # Grab text elements
        
        # Skip job-title and job-company elements
    filtered_desc = []
    for el in desc_elements:
        parent_classes = el.evaluate("(node) => node.parentElement.className")  # Get parent class
        if "job-title" not in parent_classes and "job-company" not in parent_classes:
            filtered_desc.append(el.inner_text().strip())

    job_info["description"] = "\n\n".join(filtered_desc) if filtered_desc else "❌ Description not found"


    # Applicants
    applicants_el = page.query_selector("div.about-job-line i.fa-user + span")
    job_info["applicants"] = applicants_el.inner_text().strip() if applicants_el else None

    # Locations
    location_el = page.query_selector("div.about-job-line i.fa-map-marker + span")
    job_info["locations"] = location_el.inner_text().strip() if location_el else None

    # Salary Range
    salary_el = page.query_selector("div.about-job-line i.fa-money + span")
    job_info["salary_range"] = salary_el.inner_text().strip() if salary_el else None

    # Extracting job URL
    job_info["url"] = page.url

    return job_info

def main():
    user = get_user()  # Choose user dynamically
    jobs_slugs = []

    def handle_response(response):
        if "jobsapi/_search" in response.url:
            try:
                data = response.json()
                hits = data.get("hits", {}).get("hits", [])
                for hit in hits:
                    slug = hit.get("_source", {}).get("slug")
                    if slug:
                        jobs_slugs.append(slug)
            except Exception as e:
                print("Error parsing JSON:", e)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.on("response", handle_response)

        # Load the main listing page with user's search query
        search_url = f"https://www.workingnomads.com/jobs?location=anywhere,europe&tag={user.search_query}"
        print(f"🔎 Searching for: {user.search_query}")
        page.goto(search_url)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Allow API response to be captured

        all_jobs = []
        for slug in jobs_slugs:
            job_url = f"https://www.workingnomads.com/remote-{user.search_query}-jobs?job={slug}"
            print(f"Scraping: {job_url}")
            page.goto(job_url)
            page.wait_for_load_state("networkidle")
            details = scrape_job_details(page)
            details["slug"] = slug
            all_jobs.append(details)

        browser.close()

    # Save to JSON file
    json_file = f"{user.name}_jobs.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scraping complete. Results saved to {json_file}")

    # Save to Google Sheets
    save_to_google_sheets(all_jobs, user.spreadsheet_id)

if __name__ == "__main__":
    main() """