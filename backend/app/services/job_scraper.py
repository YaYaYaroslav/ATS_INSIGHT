"""Job Posting Scraper.

Strategy, in priority order:
1. JSON-LD JobPosting (schema.org) — most reliable; used by most job boards
   for Google for Jobs, so it often works even on unfamiliar sites.
2. Site-specific CSS selectors (work.ua) — best-effort, may go stale if the
   site changes its markup.
3. Generic fallback: a readability-style heuristic that strips nav/footer/
   script and picks the block with the highest text density.
"""

import json
import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class ScraperError(Exception):
    pass


def _fetch_html(url: str) -> str:
    try:
        response = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en,uk;q=0.9"},
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as exc:
        raise ScraperError(f"The site returned an error {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        raise ScraperError(f"Could not load the page: {exc}") from exc


def _html_fragment_to_text(html_fragment: str) -> str:
    return BeautifulSoup(html_fragment, "html.parser").get_text("\n", strip=True)


def _extract_jsonld_jobposting(soup: BeautifulSoup) -> dict | None:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type")
            if item_type == "JobPosting" or (isinstance(item_type, list) and "JobPosting" in item_type):
                return item
            if "@graph" in item and isinstance(item["@graph"], list):
                for sub in item["@graph"]:
                    if isinstance(sub, dict) and sub.get("@type") == "JobPosting":
                        return sub
    return None


def _extract_work_ua(soup: BeautifulSoup) -> str | None:
    for selector in ["div#job-description", "div.card.wordwrap", "div[id*='description']", "article", "main"]:
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 200:
            return node.get_text("\n", strip=True)
    return None


def _extract_generic(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form"]):
        tag.decompose()

    best_node, best_score = None, 0
    for node in soup.find_all(["article", "main", "div", "section"]):
        text = node.get_text(" ", strip=True)
        paragraph_count = len(node.find_all("p"))
        score = len(text) + paragraph_count * 50
        if score > best_score and len(text) < 20000:
            best_score, best_node = score, node

    if best_node is not None and best_score > 300:
        return best_node.get_text("\n", strip=True)

    return soup.get_text("\n", strip=True)


def scrape_job_posting(url: str) -> dict:
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    jsonld = _extract_jsonld_jobposting(soup)
    if jsonld:
        description_html = jsonld.get("description", "")
        text = _html_fragment_to_text(description_html) if description_html else ""
        if len(text) > 100:
            return {"title": jsonld.get("title"), "raw_text": text}

    site_text = _extract_work_ua(soup) if "work.ua" in url.lower() else None

    if site_text:
        title_tag = soup.find("h1")
        return {"title": title_tag.get_text(strip=True) if title_tag else None, "raw_text": site_text}

    generic_text = _extract_generic(soup)
    if len(generic_text.strip()) < 100:
        raise ScraperError("Could not extract enough text from the page. Try pasting the job description manually.")

    title_tag = soup.find("h1")
    return {"title": title_tag.get_text(strip=True) if title_tag else None, "raw_text": generic_text}
