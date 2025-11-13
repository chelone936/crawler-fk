from scheduler.tasks import run_daily_change_report

if __name__ == "__main__":
    # Send the crawl task to the Celery worker
    run_daily_change_report.delay()
    print("Daily crawl task sent to Celery worker")
