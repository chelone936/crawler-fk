from pydantic import BaseModel
from typing import Optional

class BookOut(BaseModel):
    book_id: str
    name: str
    price_incl_tax: Optional[str]
    price_excl_tax: Optional[str]
    tax: Optional[str]
    availability: Optional[str]
    product_description: Optional[str]
    upc: Optional[str]
    number_of_reviews: Optional[int]
    image_url: Optional[str]
    product_page_url: str

class ChangeLogOut(BaseModel):
    book_id: str
    change_type: str
    timestamp: str
    old_value: dict
    new_value: dict