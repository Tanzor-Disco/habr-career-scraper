import asyncio
import re
import requests

import aiohttp
from bs4 import BeautifulSoup, Tag

HABR_CAREER_BASE_URL = "https://career.habr.com/vacancies?page="


class Vacancy:
    def __init__(
        self,
        title: str,
        company: str,
        seniority: str | None,
        work_type: str | None,
        location: str | None,
        salary: int | None,
        skills: list[str],
        vacancy_id:int
    ):
        self.title = title
        self.company = company
        self.seniority = seniority
        self.work_type = work_type
        self.location = location
        self.salary = salary
        self.skills = skills
        self.vacancy_id = vacancy_id

    def __str__(self):
        return f"(title: {self.title}, company: {self.company}, seniority: {self.seniority}, work_type: {self.work_type}, location:{self.location}, salary: {self.salary}, skills:{self.skills}, vacancy_id:{self.vacancy_id})"


def scrape_vacancy(vacancy: Tag) -> Vacancy:
    title = vacancy.select_one("a.vacancy-card__title-link")
    assert title is not None
    title = title.get_text()

    company = vacancy.select_one("a.link-comp.link-comp--appearance-dark")
    assert company is not None
    company = company.get_text()

    seniority = vacancy.select_one('.vacancy-meta .basic-chip:has(use[xlink\\:href*="#grade"]) .chip-with-icon__text')
    if seniority is not None:
        seniority = seniority.get_text()

    work_type = vacancy.select_one('.vacancy-meta .basic-chip:has(use[xlink\\:href*="#format"]) .chip-with-icon__text')
    if work_type is not None:
        work_type = work_type.get_text()

    location = vacancy.select_one(
        '.vacancy-meta .basic-chip:has(use[xlink\\:href*="#placemark"]) .chip-with-icon__text'
    )
    if location is not None:
        location = location.get_text()

    salary = None
    salary_div = vacancy.select_one("div.vacancy-card__salary")
    if salary_div is not None:
        salary_basic = salary_div.select_one(".basic-salary")
        if salary_basic is not None:
            salary = int(salary_basic.get_text().split()[1])
        salary_predicted = salary_div.select_one("span.tooltip")
        if salary_predicted is not None and salary_basic is None:
            text = salary_predicted.get_text()
            salaries = re.findall(r"\d[\d\s]*", text)
            salaries = [int(salary.replace(" ", "")) for salary in salaries]
            mean = (salaries[0] + salaries[1]) // 2
            salary = mean

    skills = []
    skills_a = vacancy.select("a.basic-chip.vacancy-card__skills-chip.basic-chip--color-ui-gray-4")
    for skill_a in skills_a:
        skills.append(skill_a.get_text())

    vacancy_link = vacancy.select_one("a.vacancy-card__backdrop-link")
    assert vacancy_link is not None

    vacancy_id = vacancy_link.get("href")
    assert vacancy_id is not None
    vacancy_id = int(str(vacancy_id).split("/")[-1])
    
    return Vacancy(title, company, seniority, work_type, location, salary, skills,vacancy_id)


def scrape_page_posts(page: str) -> list[Vacancy]:
    soup = BeautifulSoup(page, "html.parser")
    vacancies = soup.select("div.basic-section.basic-section--appearance-vacancy-card")
    vacancies_list = []
    for vacancy in vacancies:
        vacancy_obj = scrape_vacancy(vacancy)
        vacancies_list.append(vacancy_obj)
    return vacancies_list


def scrape_pages(pages: list[str]) -> list[Vacancy]:
    vacancies_list = []
    for page in pages:
        page_list = scrape_page_posts(page)
        vacancies_list.extend(page_list)
    return vacancies_list


async def async_get_page(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def async_get_pages(num_pages: int) -> list[str]:
    async with aiohttp.ClientSession() as session:
        pages = await asyncio.gather(
            *[async_get_page(session, HABR_CAREER_BASE_URL + str(curr_page+1)) for curr_page in range(num_pages)]
        )
    return pages


async def get_and_scrape() -> list[Vacancy]:
    # 70 has been experimentally measured to be the biggest number of requests that doesn't get blocked
    pages = await async_get_pages(70)
    vacancies = scrape_pages(pages)
    return vacancies

def test_sync_get_page(url:str) -> str:
    return requests.get(url).text
    
def test_sync_get_and_scrape(num_pages:int):
    pages = [test_sync_get_page(HABR_CAREER_BASE_URL + str(curr_page+1)) for curr_page in range(num_pages)]
    vacancies = scrape_pages(pages)
    return vacancies

async def test():
    vacancies = await get_and_scrape()


if __name__ == "__main__":
    asyncio.run(test())
