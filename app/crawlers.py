import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from bs4 import BeautifulSoup, Tag


async def fetch_page(
    url: str, timeout: float = 10.0
) -> Optional[httpx.Response]:
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True
    ) as client:
        try:
            response = await client.get(url)
            return response
        except httpx.HTTPError as exc:
            print(f"HTTP error occurred: {exc}")
            return None


def extract_links_and_meta(
    html: str, base_url: str, required_meta_tags: List[str]
) -> Tuple[Set[str], List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    local_links = set()
    for a in soup.find_all("a", href=True):
        if not isinstance(a, Tag):
            continue
        href = a["href"]
        if not href or not isinstance(href, str):
            continue
        if href.startswith("/"):
            local_links.add(base_url.rstrip("/") + href)
        elif href.startswith(base_url):
            local_links.add(href)

    meta_errors = []
    for tag in required_meta_tags:
        if tag.lower() == "title":
            if not soup.find("title"):
                meta_errors.append("Missing <title> tag")
        elif tag.lower().startswith("meta"):
            meta_name = tag.split(" ")[1]
            if not soup.find("meta", attrs={"name": meta_name}):
                meta_errors.append(f"Missing <meta name='{meta_name}'> tag")

        else:
            if not soup.find(tag):
                meta_errors.append(f"Missing <{tag}> tag")
    return (local_links, meta_errors)


async def crawl_site(
    root: str, max_depth: int, required_meta_tags: List[str]
) -> Dict[str, Any]:
    visted_links = set()
    broken_links = []
    meta_issues = {}

    async def crawl(url: str, depth: int):
        if depth > max_depth or url in visted_links:
            return
        visted_links.add(url)
        response = await fetch_page(url)
        if not response:
            broken_links.append(url)
            return
        links, meta_errors = extract_links_and_meta(
            response.text, root, required_meta_tags
        )
        if meta_errors:
            meta_issues[url] = meta_errors
        tasks = []
        for link in links:
            if link.startswith(root):
                tasks.append(crawl(link, depth + 1))
        if tasks:
            await asyncio.gather(*tasks)

    await crawl(root, 0)
    return {"broken_links": broken_links, "meta_issues": meta_issues}
