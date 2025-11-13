import pytest
from crawler.parser import parse_list_page, parse_book_page, normalize_price
from crawler.models import Book, ChangeLog
from crawler.fetcher import fetch
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

def test_normalize_price():
    assert normalize_price("£51.77") == "51.77"
    assert normalize_price("$100.00") == "100.00"
    assert normalize_price(None) is None

def test_parse_list_page_basic():
    html = """
    <html>
      <article class="product_pod">
        <h3><a href="book1.html" title="Book One">Book One</a></h3>
        <div class="product_price"><p class="price_color">£51.77</p></div>
      </article>
      <ul class="pager"><li class="next"><a href="page2.html">next</a></li></ul>
    </html>
    """
    books, next_page = parse_list_page(html, "https://books.toscrape.com/")
    assert books[0]["url"].endswith("book1.html")
    assert books[0]["title"] == "Book One"
    assert books[0]["price"] == "51.77"
    assert next_page.endswith("page2.html")

def test_parse_book_page_basic():
    html = """
    <html>
      <div class="product_main"><h1>Book Title</h1></div>
      <table class="table-striped">
        <tr><th>UPC</th><td>abc123</td></tr>
        <tr><th>Price (excl. tax)</th><td>£50.00</td></tr>
        <tr><th>Price (incl. tax)</th><td>£55.00</td></tr>
        <tr><th>Tax</th><td>£5.00</td></tr>
        <tr><th>Number of reviews</th><td>10</td></tr>
      </table>
      <p class="instock availability">In stock</p>
      <div id="product_description"></div>
      <p>Great book!</p>
      <div id="product_gallery"><img src="/media/cache/xx.jpg"/></div>
    </html>
    """
    book = parse_book_page(html, "https://books.toscrape.com/catalogue/book_1000/index.html")
    assert book.name == "Book Title"
    assert book.upc == "abc123"
    assert book.price_excl_tax == "50.00"
    assert book.price_incl_tax == "55.00"
    assert book.tax == "5.00"
    assert book.number_of_reviews == 10
    assert book.availability.startswith("In stock")
    assert book.product_description == "Great book!"
    assert book.image_url.endswith("xx.jpg")
    assert book.book_id == "1000"

@pytest.mark.asyncio
async def test_fetch_success():
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.url = "https://books.toscrape.com/"
    mock_response.raise_for_status = MagicMock()
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        with patch("crawler.fetcher.httpx.AsyncClient") as mock_client:
            session = mock_client.return_value
            session.get = mock_get
            text, url = await fetch(session, "https://books.toscrape.com/")
            assert text == "<html></html>"
            assert url == "https://books.toscrape.com/"

def test_book_model():
    book = Book(
        book_id="1",
        name="Test Book",
        price_incl_tax="10.00",
        price_excl_tax="9.00",
        tax="1.00",
        availability="In stock",
        product_description="A book.",
        upc="upc1",
        number_of_reviews=5,
        image_url="http://img",
        product_page_url="http://page",
        raw_html="<html></html>",
        crawl_metadata={"site": "books.toscrape"}
    )
    assert book.name == "Test Book"
    assert book.crawl_metadata["site"] == "books.toscrape"

def test_changelog_model():
    change = ChangeLog(
        book_id="1",
        change_type="insert",
        timestamp=datetime.utcnow(),
        old_value={},
        new_value={"name": "Test Book"}
    )
    assert change.change_type == "insert"
    assert change.new_value["name"] == "Test Book"

def test_hash_book_and_save_book(monkeypatch):
    from crawler.db import hash_book, save_book
    from crawler.models import Book

    # Setup a dummy book
    book = Book(
        book_id="1",
        name="Test Book",
        price_incl_tax="10.00",
        price_excl_tax="9.00",
        tax="1.00",
        availability="In stock",
        product_description="A book.",
        upc="upc1",
        number_of_reviews=5,
        image_url="http://img",
        product_page_url="http://page",
        raw_html="<html></html>",
        crawl_metadata={"site": "books.toscrape"}
    )
    # Test hash_book
    h = hash_book(book)
    assert isinstance(h, str)
    # Patch MongoDB calls in save_book
    monkeypatch.setattr("crawler.db.collection.find_one", lambda q: None)
    monkeypatch.setattr("crawler.db.collection.update_one", lambda q, u, upsert: None)
    monkeypatch.setattr("crawler.db.change_log_collection.insert_one", lambda doc: None)
    monkeypatch.setattr("crawler.db.logging", MagicMock())
    # Should not raise
    save_book(book)