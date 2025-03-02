import requests
from bs4 import BeautifulSoup

def scrape_jobfluent():
    url = 'https://www.jobfluent.com/es/empleos-remoto'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_card in soup.find_all('div', class_='panel-offer'):
        title = job_card.find('h3').a.text.strip()
        salary_tag = job_card.find('span', class_='salary')
        salary = salary_tag.text.strip() if salary_tag else 'N/A'
        # location = job_card.find('span', class_='location').text.strip()
        link = 'https://www.jobfluent.com/es/empleos' + job_card.find('a')['href']
        
        jobs.append({
            'title': title,
            'salary': salary,
            # 'location': location,
            'link': link
        })

    return jobs

if __name__ == '__main__':
    job_listings = scrape_jobfluent()
    for job in job_listings:
        print(f"Title: {job['title']}")
        # print(f"Company: {job['company']}")
        print(f"Salary: {job['salary']}")
        print(f"Link: {job['link']}")
        print('-' * 20)
    print(f"Soy concha, me voy a dormir")