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

def find_all(user, package_name="scrapers"):
    scrapers = load_scrapers(package_name)
    all_jobs = []
    for scraper_name, get_jobs in scrapers:
        jobs = get_jobs(user)
        for job in jobs:
            # Annotate each job with its source.
            if "sources" in job:
                if scraper_name not in job["sources"]:
                    job["sources"].append(scraper_name)
            else:
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

def merge_duplicate_jobs(jobs, threshold=0.8):
    merged = []
    for job in jobs:
        found = False
        for m_job in merged:
            if are_jobs_duplicates(job, m_job, threshold):
                # Merge sources lists if duplicate found.
                for src in job.get("sources", []):
                    if src not in m_job["sources"]:
                        m_job["sources"].append(src)
                found = True
                break
        if not found:
            merged.append(job)
    return merged
