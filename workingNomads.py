import json
import time
from playwright.sync_api import sync_playwright

def scrape_job_details(page):
    job_info = {}
    # Adjust these selectors as needed
    title_el = page.query_selector("h1.job-title")
    company_el = page.query_selector("div.job-company")
    desc_el = page.query_selector("p.job-desktop-description")
    applicants_el = page.query_selector("div span.about-job-line-text")
    locations_el = page.query_selector("div span.about-job-line-text")
    salary_el = page.query_selector("div span.about-job-line-text")

    job_info["title"] = title_el.inner_text().strip() if title_el else None
    job_info["company"] = company_el.inner_text().strip() if company_el else None
    job_info["description"] = desc_el.inner_text().strip() if desc_el else None
    job_info["applicants"] = applicants_el.inner_text().strip() if applicants_el else None
    job_info["locations"] = locations_el.inner_text().strip() if locations_el else None
    job_info["salary_range"] = salary_el.inner_text().strip() if salary_el else None
    return job_info

def main():
    jobs_slugs = []

    def handle_response(response):
        if "jobsapi/_search" in response.url:
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])
            for hit in hits:
                slug = hit.get("_source", {}).get("slug")
                if slug:
                    jobs_slugs.append(slug)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Intercept the JSON response for job slugs
        page.on("response", handle_response)

        # Load the main listing page
        page.goto("https://www.workingnomads.com/jobs?tag=nodejs")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Give the site time to fetch job data

        # Now visit each job detail page
        all_jobs = []
        for slug in jobs_slugs:
            job_url = f"https://www.workingnomads.com/remote-nodejs-jobs?job={slug}"
            page.goto(job_url)
            page.wait_for_load_state("networkidle")
            details = scrape_job_details(page)
            details["slug"] = slug
            all_jobs.append(details)

        browser.close()

    # Save or print the results
    print(json.dumps(all_jobs, indent=2))

if __name__ == "__main__":
    main()
