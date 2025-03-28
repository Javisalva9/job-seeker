import requests
import datetime
import os
from bs4 import BeautifulSoup
from job_schema import JobFields
from typing import List


def get_jobs(user):
    base_url = "https://www.jobfluent.com/es/empleos-remoto"
    page = 1
    jobs: List[JobFields] = []

    while True:  # Bucle infinito que se romperá cuando no haya más páginas
        url = f"{base_url}?q={user.search_query}&page={page}"  # Construye la URL con el número de página
        print(f"Scraping page: {page}, URL: {url}")  # Mensaje para seguimiento
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lanza una excepción para códigos de estado de error (4xx, 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la página {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("div", class_="panel-offer")

        if not job_cards:
            print(f"Didn't found any other offer on page {page}. Exiting...")
            break

        for i, job_card in enumerate(job_cards):
            if i >= 1 and os.environ.get("TEST_MODE"):
                break

            try:  # Usamos un try except para que no se pare el programa si hay algun anuncio que da error
                title = job_card.find("h3").a.text.strip()
                salary_tag = job_card.find("span", class_="salary")
                salary = salary_tag.text.strip() if salary_tag else "N/A"
                offer_div = job_card.find("div", class_="offer")
                data_url = offer_div.get("data-url", "") if offer_div else ""
                link = f"https://www.jobfluent.com{data_url}"

                try:  # Otro try/except para manejar errores al obtener detalles
                    responseDetail = requests.get(link)
                    responseDetail.raise_for_status()
                    detailSoup = BeautifulSoup(responseDetail.text, "html.parser")
                    location_tag = detailSoup.find("span", itemprop="address")
                    location = (
                        location_tag.text.strip() + " o en remoto" if location_tag else "Remoto"
                    )  # Mejor manejo si falta la ubicación
                    company_tag = detailSoup.find("span", itemprop="hiringOrganization")
                    company = (
                        company_tag.find("span").text.strip() if company_tag else "N/A"
                    )  # Si no encuentra la compañía
                    description_div = detailSoup.find("div", class_="offer-description-content")
                    description = (
                        description_div.find("div").text.strip() if description_div else "N/A"
                    )  # Si no encuentra descripción

                except requests.exceptions.RequestException as e:
                    print(f"Error al obtener detalles de {link}: {e}")
                    continue  # Continúa con la siguiente oferta si falla una
                except AttributeError as e:
                    print(f"Error al procesar los detalles de la oferta{link}: {e}")
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "description": description,
                        "url": link,
                        "apply_url": link,
                        "applicants": "N/A",
                        "locations": location,
                        "salary": salary,
                        "slug": "N/A",
                        "sources": [],
                        "score": "",
                        "comment": "",
                        "ai_model": "",
                        "applied": False,
                        "interview": "pending",
                        "added_date": datetime.datetime.now().isoformat(),
                    }
                )
            except AttributeError as e:
                print(f"Error al procesar la oferta: {e}")
                continue

        page += 1  # Incrementa el número de página para la siguiente iteración

    return jobs
