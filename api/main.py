from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pymongo import MongoClient, DESCENDING, ASCENDING
from dotenv import load_dotenv
import os

from .auth import get_api_key
from .schemas import BookOut, ChangeLogOut

load_dotenv()

app = FastAPI(title="Books API", version="1.0.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "default_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "books")
CHANGE_LOG_COLLECTION_NAME = os.getenv("CHANGE_LOG_COLLECTION_NAME", "change_log")

print("Before MongoClient")  # Add this
client = MongoClient(MONGO_URI)
print("After MongoClient")   # Add this
db = client[DB_NAME]
books_col = db[COLLECTION_NAME]
changes_col = db[CHANGE_LOG_COLLECTION_NAME]

@app.get("/books", response_model=list[BookOut])
@limiter.limit("100/hour")
async def get_books(
    request:Request,
    category: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    rating: int = Query(None),
    sort_by: str = Query("rating"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    api_key: str = Depends(get_api_key)
):
    query = {}
    if category:
        query["crawl_metadata.category"] = category
    if min_price or max_price:
        price_field = "price_incl_tax"
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query[price_field] = price_query
    if rating:
        query["crawl_metadata.rating"] = rating

    sort_map = {
        "rating": ("crawl_metadata.rating", DESCENDING),
        "price": ("price_incl_tax", ASCENDING),
        "reviews": ("number_of_reviews", DESCENDING)
    }
    sort_field, sort_dir = sort_map.get(sort_by, ("crawl_metadata.rating", DESCENDING))

    skip = (page - 1) * page_size
    cursor = books_col.find(query).sort(sort_field, sort_dir).skip(skip).limit(page_size)
    results = [BookOut(**{**doc, "book_id": str(doc["book_id"])}) for doc in cursor]
    return results

@app.get("/books/{book_id}", response_model=BookOut)
@limiter.limit("100/hour")
async def get_book(    request:Request,book_id: str, api_key: str = Depends(get_api_key)):
    doc = books_col.find_one({"book_id": book_id})
    if not doc:
        raise HTTPException(404, "Book not found")
    return BookOut(**{**doc, "book_id": str(doc["book_id"])})

@app.get("/changes", response_model=list[ChangeLogOut])
@limiter.limit("100/hour")
async def get_changes(    request:Request,
    limit: int = Query(20, le=100),
    api_key: str = Depends(get_api_key)
):
    cursor = changes_col.find().sort("timestamp", DESCENDING).limit(limit)
    results = [
        ChangeLogOut(
            book_id=str(doc.get("book_id")),
            change_type=doc.get("change_type"),
            timestamp=doc.get("timestamp").isoformat() if doc.get("timestamp") else "",
            old_value=doc.get("old_value", {}),
            new_value=doc.get("new_value", {}),
        )
        for doc in cursor
    ]
    return results

@app.get("/")
def root():
    return {"message": "Books API is running. See /docs for documentation."}