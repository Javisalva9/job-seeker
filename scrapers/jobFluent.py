import requests
import datetime
import os
from bs4 import BeautifulSoup
from job_schema import JobFields
from typing import List


def get_jobs(user):
    url = f"https://www.jobfluent.com/es/empleos-remoto?q={user.search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs: List[JobFields] = []

    for i, job_card in enumerate(soup.find_all("div", class_="panel-offer")):
        if i >= 3 and os.environ.get("TEST_MODE"):
            break
        title = job_card.find("h3").a.text.strip()
        salary_tag = job_card.find("span", class_="salary")
        salary = salary_tag.text.strip() if salary_tag else "N/A"
        offer_div = job_card.find("div", class_="offer")
        data_url = offer_div.get("data-url", "") if offer_div else ""
        link = f"https://www.jobfluent.com{data_url}"

        responseDetail = requests.get(link)
        detailSoup = BeautifulSoup(responseDetail.text, "html.parser")
        location = detailSoup.find("span", itemprop="address").text.strip() + " o en remoto"
        company = detailSoup.find("span", itemprop="hiringOrganization").find("span").text.strip()
        description = detailSoup.find("div", class_="offer-description-content").find("div").text.strip()

        jobs.append(
            {
                "title": title,
                "company": company,
                "description": description,
                "url": link,
                "apply_url": link,
                "applicants": "N/A",
                "locations": location,
                "salary_range": salary,
                "slug": "N/A",
                "sources": [],
                "score": "",
                "comment": "",
                "ai_model": "",
                "applied": False,
                "interview_status": "pending",
                "added_date": datetime.datetime.now().isoformat(),
            }
        )

    return jobs
