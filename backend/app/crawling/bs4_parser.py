"""BeautifulSoup helpers for parsing HTML from career pages."""

from bs4 import BeautifulSoup


def extract_json_ld(html: str) -> list[dict]:
    """Extract JSON-LD structured data blocks from HTML.

    Career pages often expose JobPosting schema.org objects via JSON-LD.
    """
    soup = BeautifulSoup(html, "lxml")
    results: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json

            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
        except (ValueError, TypeError):
            continue
    return results


def extract_jobposting_from_json_ld(html: str) -> list[dict]:
    """Extract JobPosting objects from JSON-LD in HTML."""
    jobs: list[dict] = []
    for block in extract_json_ld(html):
        if isinstance(block, dict):
            types = block.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if "JobPosting" in types:
                jobs.append(block)
        elif isinstance(block, list):
            for item in block:
                if isinstance(item, dict):
                    types = item.get("@type", [])
                    if isinstance(types, str):
                        types = [types]
                    if "JobPosting" in types:
                        jobs.append(item)
    return jobs


def find_links(html: str, base_url: str, keyword: str = "job") -> list[str]:
    """Find anchor links containing a keyword in href or text."""
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        full_url = urljoin(base_url, href)
        if keyword.lower() in href.lower() or keyword.lower() in text.lower():
            links.append(full_url)
    return links