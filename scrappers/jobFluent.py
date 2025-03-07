import requests
from bs4 import BeautifulSoup
from job_schema import JobFields
from typing import List


def scrape_jobfluent():
    url = 'https://www.jobfluent.com/es/empleos-remoto'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs: List[JobFields] = []
    for job_card in soup.find_all('div', class_='panel-offer'):
        title = job_card.find('h3').a.text.strip()
        salary_tag = job_card.find('span', class_='salary')
        salary = salary_tag.text.strip() if salary_tag else 'N/A'
        link = 'https://www.jobfluent.com' + \
            job_card.find('div', class_='offer')['data-url']

        responseDetail = requests.get(link)
        detailSoup = BeautifulSoup(responseDetail.text, 'html.parser')
        location = detailSoup.find('span', itemprop='address').text.strip() + ' o en remoto'
        company = detailSoup.find(
            'span', itemprop='hiringOrganization').find('span').text.strip()
        description = detailSoup.find(
            'div', class_='offer-description-content').find('div').text.strip()

        jobs.append({
            'title': title,
            'company':  company,
            'description': description,
            'url': link,
            'apply_url': link,
            'applicants': 'N/A',
            'locations': location,
            'salary_range': salary,
            'slug': 'N/A'
        })

        for job in jobs:
            print(f"Title: {job['title']}")
            print(f"company: {job['company']}")
            print(f"locations: {job['locations']}")
            print(f"Salary: {job['salary_range']}")
            print(f"Link: {job['url']}")
            print('-' * 20)

    return jobs


if __name__ == '__main__':
    job_listings = scrape_jobfluent()
    for job in job_listings:
        print(f"Title: {job['title']}")
        print(f"description: {job['description']}")
        print(f"Salary: {job['salary']}")
        print(f"Link: {job['link']}")
        print('-' * 20)
    print(f"Soy concha, me voy a dormir")
