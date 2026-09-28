#!/usr/bin/env python3
"""Enrich confirmed book seeds with Google Books metadata.

Google Books Volumes API supports title/author searches and returns volume
metadata including descriptions, categories and imageLinks. This script keeps
the Amazon ASIN/ISBN as the stable catalog identity and treats Google Books
metadata as enrichment only.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "books.json"
OUTPUT = ROOT / "data" / "books.json"
API = "https://www.googleapis.com/books/v1/volumes"

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "JagdishAroraBookCatalog/1.0 (+https://techbaggg.github.io/)"
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def score(seed, item):
    info = item.get("volumeInfo", {})
    title = normalize(info.get("title", ""))
    target = normalize(seed["title"])
    score = 0
    if title == target:
        score += 100
    elif target in title or title in target:
        score += 60
    authors = " ".join(info.get("authors", []))
    if "arora" in normalize(authors):
        score += 30
    if seed.get("isbn") and seed["isbn"] in json.dumps(info.get("industryIdentifiers", [])):
        score += 50
    return score

def enrich(seed):
    q = "intitle:" + seed["title"] + " inauthor:Jagdish Arora"
    params = urllib.parse.urlencode({"q": q, "maxResults": 10, "printType": "books"})
    try:
        payload = fetch_json(API + "?" + params)
    except Exception as exc:
        seed["google_books_status"] = "error"
        seed["google_books_error"] = str(exc)
        return seed

    items = payload.get("items", [])
    if not items:
        seed["google_books_status"] = "not-found"
        return seed

    item = max(items, key=lambda x: score(seed, x))
    info = item.get("volumeInfo", {})
    if score(seed, item) < 50:
        seed["google_books_status"] = "low-confidence"
        return seed

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
    seed["cover"] = (info.get("imageLinks") or {}).get("thumbnail")
    seed["google_books_url"] = info.get("infoLink")
    seed["google_books_status"] = "enriched"
    return seed

payload=json.loads(INPUT.read_text(encoding="utf-8"))
for book in payload.get("books", []):
    enrich(book)
    time.sleep(0.2)

payload["generated_at"] = datetime.now(timezone.utc).isoformat()
payload["source"] = "Amazon-confirmed seeds enriched with Google Books Volumes API metadata."
OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Enriched", len(payload.get("books", [])), "book seeds.")
