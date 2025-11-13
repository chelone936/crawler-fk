import httpx
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
async def fetch(session: httpx.AsyncClient, url: str):
    """
    Fetch HTML content from a URL with retry logic for transient errors.
    Returns a tuple (text, final_url) so callers can resolve relative links.
    """
    response = await session.get(url, timeout=30)
    response.raise_for_status()
    return response.text, str(response.url)
