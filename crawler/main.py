import asyncio
import httpx
from fetcher import fetch
from parser import parse_list_page, parse_book_page
from db import save_book

async def crawl(start_urls, max_pages=None):
    """
    Crawl the listing pages starting from start_urls, follow pagination,
    collect product page URLs, fetch product pages and persist Book models.
    """
    async with httpx.AsyncClient() as session:
        to_visit = list(start_urls)
        visited_list_pages = set()
        book_urls = set()
        pages_crawled = 0

        while to_visit:
            page = to_visit.pop(0)
            # simple dedupe of list pages
            if page in visited_list_pages:
                continue
            html, final_url = await fetch(session, page)
            visited_list_pages.add(final_url)
            pages_crawled += 1

            books, next_page = parse_list_page(html, final_url)
            for b in books:
                book_urls.add(b["url"])

            if next_page and (max_pages is None or pages_crawled < max_pages):
                if next_page not in visited_list_pages:
                    to_visit.append(next_page)

        # fetch product pages concurrently (bounded concurrency recommended for large crawls)
        sem = asyncio.Semaphore(20)
        async def _fetch_and_parse(u):
            async with sem:
                html, final = await fetch(session, u)
                book = parse_book_page(html, final)
                save_book(book)

        await asyncio.gather(*[_fetch_and_parse(u) for u in sorted(book_urls)])

async def crawl_book_urls():
    start_urls = ["https://books.toscrape.com/"]
    await crawl(start_urls)

if __name__ == "__main__":
    asyncio.run(crawl_book_urls())
