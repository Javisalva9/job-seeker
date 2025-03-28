import pkgutil
import importlib
import difflib


def load_scrapers(package_name="scrapers"):
    scrapers = []
    package = importlib.import_module(package_name)
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{name}")
        if hasattr(module, "get_jobs"):
            # Use a variable SCRAPER_NAME if defined, otherwise the module name.
            scraper_name = getattr(module, "SCRAPER_NAME", name)
            scrapers.append((scraper_name, module.get_jobs))
    return scrapers


def scrape_all(user, package_name="scrapers"):
    scrapers = load_scrapers(package_name)
    all_jobs = []
    for scraper_name, get_jobs in scrapers:
        jobs = get_jobs(user)
        print("✅ Finished scraping for", scraper_name)

        for job in jobs:
            job["sources"] = [scraper_name]
            all_jobs.append(job)
    unique_jobs = merge_duplicate_jobs(all_jobs)
    return unique_jobs


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def are_jobs_duplicates(job1, job2, threshold=0.8):
    title_sim = similar(job1.get("title", "").lower(), job2.get("title", "").lower())
    company_sim = similar(job1.get("company", "").lower(), job2.get("company", "").lower())
    return title_sim >= threshold and company_sim >= threshold


def merge_duplicate_jobs(all_jobs):
    merged_jobs = {}
    for job in all_jobs:
        key = (job["title"].lower(), job["company"].lower())
        if key in merged_jobs:
            # Merge sources while maintaining uniqueness
            merged_jobs[key]["sources"] = list(set(merged_jobs[key]["sources"] + job["sources"]))
        else:
            merged_jobs[key] = job.copy()
    return list(merged_jobs.values())
