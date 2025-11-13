from scheduler.celery_app import app
from crawler.main import crawl_book_urls
from crawler.db import generate_daily_change_report

import asyncio

@app.task
def run_daily_crawl():
    """
    Celery task to run the book scraper daily.
    """
    asyncio.run(crawl_book_urls())


@app.task
def run_daily_change_report():
    """
    Celery task to generate daily change report.
    """
    json_file, csv_file = generate_daily_change_report()
    if json_file and csv_file:
        print(f"Daily report generated: {json_file}, {csv_file}")
