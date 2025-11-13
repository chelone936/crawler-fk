from celery import Celery
from celery.schedules import crontab

app = Celery(
    "book_crawler",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=['scheduler.tasks']
)

app.conf.beat_schedule = {
    "daily-book-crawl": {
        "task": "scheduler.tasks.run_daily_crawl",
        "schedule": crontab(hour=2, minute=0),  # Daily crawl at 2 AM UTC
    },
    "daily-change-report": {
        "task": "scheduler.tasks.run_daily_change_report",
        "schedule": crontab(hour=3, minute=0),  # Generate report 1 hour after crawl
    },
}

app.conf.timezone = "UTC"
