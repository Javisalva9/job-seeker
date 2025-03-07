from playwright.sync_api import sync_playwright
import time

def scrape_job_details(page):
    job_info = {}
    title_el = page.query_selector("h1.job-title")
    job_info["title"] = title_el.inner_text().strip() if title_el else None

    company_el = page.query_selector("div.job-company span a")
    job_info["company"] = company_el.inner_text().strip() if company_el else None

    job_el = page.query_selector("div.job")
    desc_elements = job_el.query_selector_all("p, ul, li")
    filtered_desc = []
    for el in desc_elements:
        parent_classes = el.evaluate("(node) => node.parentElement.className")
        if "job-title" not in parent_classes and "job-company" not in parent_classes:
            filtered_desc.append(el.inner_text().strip())
    job_info["description"] = "\n\n".join(filtered_desc) if filtered_desc else "❌ Description not found"

    applicants_el = page.query_selector("div.about-job-line i.fa-user + span")
    job_info["applicants"] = applicants_el.inner_text().strip() if applicants_el else None

    location_el = page.query_selector("div.about-job-line i.fa-map-marker + span")
    job_info["locations"] = location_el.inner_text().strip() if location_el else None

    salary_el = page.query_selector("div.about-job-line i.fa-money + span")
    job_info["salary_range"] = salary_el.inner_text().strip() if salary_el else None

    job_info["url"] = page.url
    return job_info

def getWorkNomads(user):
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

    workNomadsJobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.on("response", handle_response)
        search_url = f"https://www.workingnomads.com/jobs?location=anywhere,europe&tag={user.search_query}"
        print(f"🔎 Searching for: {user.search_query}")
        page.goto(search_url)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # wait for API responses

        for slug in jobs_slugs:
            job_url = f"https://www.workingnomads.com/remote-{user.search_query}-jobs?job={slug}"
            print(f"Scraping: {job_url}")
            page.goto(job_url)
            page.wait_for_load_state("networkidle")
            details = scrape_job_details(page)
            details["slug"] = slug
            workNomadsJobs.append(details)

        browser.close()
    return workNomadsJobs
