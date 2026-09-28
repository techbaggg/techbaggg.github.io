#!/usr/bin/env python3
"""Merge Amazon discoveries and enrich the book catalog.

Pipeline:
1. Read data/amazon-discovered-books.json (fresh Amazon ASIN discoveries).
2. Preserve existing curated/enriched data in data/books.json.
3. For new ASINs, try the Amazon product page for a title/cover.
4. Enrich titled books with Google Books metadata when a confident match exists.
5. Write one deduplicated books.json used by the website.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCOVERED = ROOT / "data" / "amazon-discovered-books.json"
OUTPUT = ROOT / "data" / "books.json"
GOOGLE_API = "https://www.googleapis.com/books/v1/volumes"
AUTHOR = "Jagdish Krishanlal Arora"

def fetch_text(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; JagdishAroraBookCatalog/1.0; +https://techbaggg.github.io/)"
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def fetch_json(url):
    return json.loads(fetch_text(url))

def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def amazon_title(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        source = fetch_text(url)
    except Exception:
        return None, None

    patterns = [
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
        r'<title[^>]*>(.*?)</title>'
    ]
    title = None
    for pattern in patterns:
        match = re.search(pattern, source, re.I | re.S)
        if match:
            title = html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
            break

    if not title:
        return None, None

    title = re.sub(r"\s*[:\-]\s*Amazon\.com.*$", "", title, flags=re.I).strip()
    title = re.sub(r"\s*\|\s*Amazon.*$", "", title, flags=re.I).strip()

    cover = None
    cover_patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']'
    ]
    for pattern in cover_patterns:
        match = re.search(pattern, source, re.I | re.S)
        if match:
            cover = html.unescape(match.group(1)).strip()
            break
    return title or None, cover

def google_score(seed, item):
    info = item.get("volumeInfo", {})
    title = normalize(info.get("title", ""))
    target = normalize(seed.get("title", ""))
    score = 0
    if title and target == title:
        score += 100
    elif target and (target in title or title in target):
        score += 65

    authors = normalize(" ".join(info.get("authors", [])))
    if "arora" in authors:
        score += 30

    isbn = seed.get("isbn")
    identifiers = json.dumps(info.get("industryIdentifiers", []))
    if isbn and isbn in identifiers:
        score += 50
    return score

def enrich_google(seed):
    title = seed.get("title")
    if not title or title.startswith("Amazon edition "):
        seed["google_books_status"] = "no-title"
        return seed

    query = urllib.parse.urlencode({
        "q": f'intitle:{title} inauthor:Jagdish Arora',
        "maxResults": 10,
        "printType": "books"
    })
    try:
        payload = fetch_json(GOOGLE_API + "?" + query)
    except Exception as exc:
        seed["google_books_status"] = "error"
        seed["google_books_error"] = str(exc)
        return seed

    items = payload.get("items", [])
    if not items:
        seed["google_books_status"] = "not-found"
        return seed

    item = max(items, key=lambda x: google_score(seed, x))
    confidence = google_score(seed, item)
    if confidence < 50:
        seed["google_books_status"] = "low-confidence"
        return seed

    info = item.get("volumeInfo", {})
    seed["google_books_id"] = item.get("id")
    seed["title"] = info.get("title") or seed["title"]
    seed["subtitle"] = info.get("subtitle")
    seed["authors"] = info.get("authors", [])
    seed["description"] = info.get("description")
    seed["publishedDate"] = info.get("publishedDate")
    seed["pageCount"] = info.get("pageCount")
    seed["categories"] = info.get("categories", [])
    seed["publisher"] = info.get("publisher")
    seed["language"] = info.get("language")
    seed["industryIdentifiers"] = info.get("industryIdentifiers", [])
    seed["cover"] = seed.get("cover") or (info.get("imageLinks") or {}).get("thumbnail")
    seed["google_books_url"] = info.get("infoLink")
    seed["google_books_status"] = "enriched"
    return seed

def slugify(title, asin):
    value = normalize(title)
    value = re.sub(r"\s+", "-", value).strip("-")
    return (value[:90] or f"amazon-{asin.lower()}")

parser = argparse.ArgumentParser()\nparser.add_argument("--ci", action="store_true", help="Run in CI mode.")\nparser.add_argument("--force", action="store_true", help="Re-run Google Books enrichment for existing entries.")\nargs = parser.parse_args()\n\nexisting_payload = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {"books": []}
existing = {book.get("asin"): book for book in existing_payload.get("books", []) if book.get("asin")}

discovered_payload = json.loads(DISCOVERED.read_text(encoding="utf-8"))
discovered = discovered_payload.get("books", [])

# Keep curated books even if Amazon's latest discovery run does not contain them.
books = dict(existing)

for item in discovered:
    asin = item.get("asin")
    if not asin:
        continue
    if asin not in books:
        books[asin] = {
            "asin": asin,
            "title": None,
            "author": AUTHOR,
            "genre": "other",
            "amazon_url": item.get("amazon_url") or f"https://www.amazon.com/dp/{asin}",
            "google_books_status": "pending"
        }
    else:
        books[asin]["amazon_url"] = item.get("amazon_url") or books[asin].get("amazon_url")

new_count = 0
force = "--force" in sys.argv

for book in books.values():
    if not book.get("title"):
        title, cover = amazon_title(book["asin"])
        if title:
            book["title"] = title
            book["amazon_title_status"] = "found"
            if cover and not book.get("cover"):
                book["cover"] = cover
        else:
            book["title"] = f"Amazon edition {book['asin']}"
            book["amazon_title_status"] = "unavailable"
        new_count += 1
        time.sleep(0.15)

    if not book.get("slug"):
        book["slug"] = slugify(book["title"], book["asin"])

    # Google enrichment is additive; never overwrite curated ISBNs.
    if force or book.get("google_books_status") in (None, "pending", "no-title"):
        enrich_google(book)
        time.sleep(0.2)

payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source": "Amazon author-page discoveries merged with curated seeds and enriched with Amazon/Google Books metadata.",
    "discovered_count": len(discovered),
    "catalog_count": len(books),
    "books": sorted(books.values(), key=lambda x: (normalize(x.get("title", "")), x.get("asin", "")))
}
OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Catalog contains {len(books)} unique ASINs; processed {new_count} records for metadata.")
