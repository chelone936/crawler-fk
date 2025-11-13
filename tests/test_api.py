# Python
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, call

from crawler.main import crawl

@pytest_asyncio.fixture
def mock_fetch():
    with patch("crawler.main.fetch", new_callable=AsyncMock) as mock:
        yield mock

@pytest_asyncio.fixture
def mock_parse_list_page():
    with patch("crawler.main.parse_list_page") as mock:
        yield mock

@pytest_asyncio.fixture
def mock_parse_book_page():
    with patch("crawler.main.parse_book_page") as mock:
        yield mock

@pytest_asyncio.fixture
def mock_save_book():
    with patch("crawler.main.save_book") as mock:
        yield mock

@pytest.mark.asyncio
async def test_crawl_single_page(
    mock_fetch, mock_parse_list_page, mock_parse_book_page, mock_save_book
):
    # Setup mocks
    mock_fetch.return_value = ("<html>list</html>", "https://books.toscrape.com/")
    mock_parse_list_page.return_value = (
        [{"url": "https://books.toscrape.com/book1.html"}], None
    )
    mock_fetch.side_effect = [
        ("<html>list</html>", "https://books.toscrape.com/"),
        ("<html>book</html>", "https://books.toscrape.com/book1.html"),
    ]
    mock_parse_book_page.return_value = {"book_id": "book1"}
    
    await crawl(["https://books.toscrape.com/"])
    
    assert mock_fetch.call_count == 2
    mock_parse_list_page.assert_called_once()
    mock_parse_book_page.assert_called_once_with("<html>book</html>", "https://books.toscrape.com/book1.html")
    mock_save_book.assert_called_once_with({"book_id": "book1"})

@pytest.mark.asyncio
async def test_crawl_pagination(
    mock_fetch, mock_parse_list_page, mock_parse_book_page, mock_save_book
):
    # Setup mocks for two pages
    mock_fetch.side_effect = [
        ("<html>list1</html>", "https://books.toscrape.com/"),
        ("<html>list2</html>", "https://books.toscrape.com/page2.html"),
        ("<html>book1</html>", "https://books.toscrape.com/book1.html"),
        ("<html>book2</html>", "https://books.toscrape.com/book2.html"),
    ]
    mock_parse_list_page.side_effect = [
        (
            [{"url": "https://books.toscrape.com/book1.html"}],
            "https://books.toscrape.com/page2.html",
        ),
        (
            [{"url": "https://books.toscrape.com/book2.html"}],
            None,
        ),
    ]
    mock_parse_book_page.side_effect = [
        {"book_id": "book1"},
        {"book_id": "book2"},
    ]
    
    await crawl(["https://books.toscrape.com/"])
    
    assert mock_fetch.call_count == 4
    assert mock_parse_list_page.call_count == 2
    assert mock_parse_book_page.call_count == 2
    assert mock_save_book.call_count == 2

@pytest.mark.asyncio
async def test_crawl_no_books(
    mock_fetch, mock_parse_list_page, mock_parse_book_page, mock_save_book
):
    mock_fetch.return_value = ("<html>list</html>", "https://books.toscrape.com/")
    mock_parse_list_page.return_value = ([], None)
    
    await crawl(["https://books.toscrape.com/"])
    
    mock_parse_book_page.assert_not_called()
    mock_save_book.assert_not_called()

@pytest.mark.asyncio
async def test_crawl_max_pages(
    mock_fetch, mock_parse_list_page, mock_parse_book_page, mock_save_book
):
    # Setup mocks for three pages, but max_pages=2
    mock_fetch.side_effect = [
        ("<html>list1</html>", "https://books.toscrape.com/"),
        ("<html>list2</html>", "https://books.toscrape.com/page2.html"),
        # Should not fetch page3
        ("<html>book1</html>", "https://books.toscrape.com/book1.html"),
        ("<html>book2</html>", "https://books.toscrape.com/book2.html"),
    ]
    mock_parse_list_page.side_effect = [
        (
            [{"url": "https://books.toscrape.com/book1.html"}],
            "https://books.toscrape.com/page2.html",
        ),
        (
            [{"url": "https://books.toscrape.com/book2.html"}],
            "https://books.toscrape.com/page3.html",
        ),
    ]
    mock_parse_book_page.side_effect = [
        {"book_id": "book1"},
        {"book_id": "book2"},
    ]
    
    await crawl(["https://books.toscrape.com/"], max_pages=2)
    
    assert mock_fetch.call_count == 4
    assert mock_parse_list_page.call_count == 2
    assert mock_parse_book_page.call_count == 2
    assert mock_save_book.call_count == 2