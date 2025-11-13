from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from models import Book

def parse_list_page(html: str, base_url: str):
    """
    Parse a paginated list page (books.toscrape list).
    Returns (books, next_page_url)
    books: list of dicts with keys: url, title, price
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for article in soup.select("article.product_pod"):
        a = article.select_one("h3 a")
        if not a:
            continue
        href = a.get("href")
        book_url = urljoin(base_url, href)
        title = a.get("title") or a.text.strip()
        price_tag = article.select_one(".product_price .price_color")
        price = price_tag.text.strip() if price_tag else None
        books.append({"url": book_url, "title": title, "price": price})

    next_a = soup.select_one("ul.pager li.next a")
    next_page = urljoin(base_url, next_a["href"]) if next_a and next_a.get("href") else None
    return books, next_page

def parse_book_page(html: str, page_url: str):
    """
    Parse an individual book product page from books.toscrape and return models.Book
    """
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("div.product_main h1")
    title = title_tag.text.strip() if title_tag else None

    # Table of product information
    upc = None
    price_excl = None
    price_incl = None
    tax = None
    num_reviews = None
    for tr in soup.select("table.table-striped tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue
        key = th.text.strip()
        val = td.text.strip()
        if key == "UPC":
            upc = val
        elif key == "Price (excl. tax)":
            price_excl = val
        elif key == "Price (incl. tax)":
            price_incl = val
        elif key == "Tax":
            tax = val
        elif key == "Number of reviews":
            try:
                num_reviews = int(val)
            except Exception:
                num_reviews = None

    avail_tag = soup.select_one("p.instock.availability")
    availability = " ".join(avail_tag.stripped_strings) if avail_tag else None

    desc = None
    desc_heading = soup.find(id="product_description")
    if desc_heading:
        p = desc_heading.find_next_sibling("p")
        if p:
            desc = p.text.strip()

    img = soup.select_one("#product_gallery img")
    image_url = urljoin(page_url, img["src"]) if img and img.get("src") else None

    # attempt to derive an ID from URL like "..._1000/index.html"
    book_id = None
    m = re.search(r"_([0-9]+)(?:/index\.html)?$", page_url)
    if m:
        book_id = m.group(1)

    book = Book(
        book_id=book_id,
        name=title or "",
        price_incl_tax=price_incl,
        price_excl_tax=price_excl,
        tax=tax,
        availability=availability,
        product_description=desc,
        upc=upc,
        number_of_reviews=num_reviews,
        image_url=image_url,
        product_page_url=page_url,
        raw_html=html,
        crawl_metadata={"site": "books.toscrape", "parsed_from": "product_page"},
    )
    return book