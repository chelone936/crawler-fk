from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Book(BaseModel):
    book_id: Optional[str] = None
    name: str
    price_incl_tax: Optional[str] = None
    price_excl_tax: Optional[str] = None
    tax: Optional[str] = None
    availability: Optional[str] = None
    product_description: Optional[str] = None
    upc: Optional[str] = None
    number_of_reviews: Optional[int] = None
    image_url: Optional[str] = None
    product_page_url: Optional[str] = None
    raw_html: Optional[str] = None
    crawl_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        orm_mode = True
