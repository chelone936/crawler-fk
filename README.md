## Overview

crawler-fk is a book data crawler and change tracking system designed to fetch, parse, and monitor book information from online sources. It provides an API for querying book details and change logs, and generates daily reports in CSV and JSON formats.

## Features

* Book Data Crawling: Fetches book data including price, description, reviews, and more.
* Change Tracking: Detects and logs changes in book data over time.
* API Access: FastAPI-based API for querying books and change logs.
* Daily Reports: Generates daily CSV/JSON reports of detected changes.
* Rate Limiting & API Key Security: Protects endpoints with rate limits and API key authentication.
* Celery Scheduler: Automates periodic crawling and reporting.


## Project Structure

requirements.txt     → Python dependencies  
README.md            → Project documentation  

api/                 → FastAPI application  
│── main.py          → API endpoints  
│── auth.py          → API key authentication  
│── schemas.py       → Pydantic models for API  

crawler/             → Crawling and parsing logic  
│── main.py          → Entry point for crawling  
│── fetcher.py       → Fetches raw HTML  
│── parser.py        → Parses HTML to extract data  
│── db.py            → Database operations  
│── models.py        → Data models  

scheduler/           → Celery beat and periodic tasks  
reports/             → Daily change reports (CSV/JSON)  
data/                → Raw or processed data storage  
logs/                → Log files  



## Installation

1. Clone the repository:
   git clone https://github.com/chelone936/crawler-fk.git
   
   cd crawler-fk

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment:
   Setup your .env file in the root folder with:
   - MONGO_URI = YOUR_MONGO_DB_URI
   - DB_NAME = DATABASE_NAME
   - COLLECTION_NAME = COLLECTION_NAME
   - API_KEY = MOCK_API_KEY FOR THE API

## Usage

1. Scheduler
   Start Celery worker and beat for periodic crawling:
   celery -A scheduler worker --loglevel=info
   celery -A scheduler beat --loglevel=info

2. Setup Redis with Docker
    docker run --name redis -p 6379:6379 -d redis

3. Launch the test crawling task by running send_test.py in the scheduler folder

4. Start the API Server
   Launch the FastAPI server:
   uvicorn api.main:app --reload
   Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

5. Reports
   Daily reports are generated in the reports/ directory as CSV and JSON files, for example:

   * reports/daily_changes_YYYYMMDD_HHMMSS.csv
   * reports/daily_changes_YYYYMMDD_HHMMSS.json

## API Endpoints

* GET /books/{book_id}: Get details for a specific book (BookOut in api/schemas.py)
* GET /changes: Get recent change logs (ChangeLogOut in api/schemas.py)
* GET /: Health check

Go to /docs for the swagger documentation

## Data Models

* BookOut (api/schemas.py): Book details
* ChangeLogOut (api/schemas.py): Change log entry

## Configuration

* Environment Variables: Set in .env (database URI, API keys, etc)
* Rate Limiting: Configured via limiter in api/main.py
* Authentication: API key required for protected endpoints (auth.py)
