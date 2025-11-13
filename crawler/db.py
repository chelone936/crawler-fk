from pymongo import MongoClient
from models import Book
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  
DB_NAME = os.getenv("DB_NAME", "default_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "books")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_book(book: Book):
    """
    Insert or update a book record in MongoDB.
    Uses upsert to avoid duplicates.
    """
    collection.update_one(
        {"book_id": book.book_id},
        {"$set": book.dict()},
        upsert=True
    )
