import asyncio

from database.database import Database
from scraper.scraper import get_and_scrape, test_sync_get_and_scrape


async def main():
    vacancies = test_sync_get_and_scrape(2)  # for tests only
    # vacancies = await get_and_scrape() #correct way
    print(f"scraped {len(vacancies)} vacancies")

    database = Database()
    print("database created")


asyncio.run(main())
