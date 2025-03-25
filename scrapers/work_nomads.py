from playwright.sync_api import sync_playwright
from job_schema import JobFields
import os
import datetime


def formatJobDetails(page, source) -> JobFields:
    locations_raw = source.get("locations", [])
    if isinstance(locations_raw, list):
        locations_str = ", ".join(locations_raw)
    else:
        locations_str = str(locations_raw).strip()

    # Get the apply_url and determine which URL to use as display_url
    apply_url = source.get("apply_url", "").strip()
    display_url = apply_url if apply_url else page.url

    job_info: JobFields = {
        "title": source.get("title", "").strip(),
        "company": source.get("company", "").strip(),
        "description": "",  # we'll fill this in
        "url": display_url,
        "apply_url": apply_url,
        "applicants": source.get("number_of_applicants", 0),
        "locations": locations_str,
        "salary_range": source.get("salary_range", "").strip(),
        "slug": source.get("slug", "").strip(),
        "sources": [],
        "score": "",
        "comment": "",
        "ai_model": "",
        "applied": False,
        "interview_status": "pending",
        "added_date": datetime.datetime.now().isoformat(),
    }
    job_el = page.query_selector("div.job")
    if job_el:
        desc_elements = job_el.query_selector_all("p, ul, li")
        filtered_desc = []
        for el in desc_elements:
            parent_classes = el.evaluate("(node) => node.parentElement.className")
            if "job-title" not in parent_classes and "job-company" not in parent_classes:
                filtered_desc.append(el.inner_text().strip())
        job_info["description"] = "\n\n".join(filtered_desc) if filtered_desc else "❌ Description not found"
    else:
        job_info["description"] = "❌ Description not found"
    return job_info


def get_jobs(user):
    jobs_data = []

    def handle_response(response):
        if "jobsapi/_search" in response.url:
            try:
                data = response.json()
                hits = data.get("hits", {}).get("hits", [])
                jobs_data.extend(hits)
            except Exception:
                print("Error parsing JSON:")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", handle_response)
        search_url = f"https://www.workingnomads.com/jobs?location=anywhere,europe&tag={user.search_query}"
        page.goto(search_url)
        page.wait_for_load_state("networkidle")
        browser.close()

    workNomadsJobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i, hit in enumerate(jobs_data):
            if i >= 3 and os.environ.get("TEST_MODE"):
                break
            source = hit.get("_source", {})
            slug = source.get("slug")
            if slug:
                job_url = f"https://www.workingnomads.com/remote-{user.search_query}-jobs?job={slug}"
                page.goto(job_url)
                page.wait_for_load_state("networkidle")
                job_details = formatJobDetails(page, source)
                workNomadsJobs.append(job_details)
        browser.close()
    return workNomadsJobs
