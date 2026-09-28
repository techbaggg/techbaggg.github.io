#!/usr/bin/env python3
"""Generate individual book pages from data/books.json.

Pages without a trustworthy book title are kept as noindex utility pages and
are excluded from the sitemap. Duplicate editions can point to a canonical
book page without competing in search.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.json"
BOOKS = ROOT / "books"
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://techbaggg.github.io"

def esc(value):
    return html.escape(str(value or ""), quote=True)

def slugify(value):
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return s[:90] or "book"

def unique_slug(book, used):
    base = slugify(book.get("slug") or book.get("title") or "book")
    slug = base
    if slug in used:
        slug = f"{base}-{book.get('asin','').lower()}"
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug

def clean_title(book):
    title = (book.get("title") or "").strip()
    if not title:
        return ""
    if title.lower().startswith("amazon edition"):
        return ""
    if title.lower() == "amazon.com":
        return ""
    if title.lower().startswith("amazon.com:"):
        return ""
    return title

def is_indexable(book):
    return bool(clean_title(book))

def canonical_slug(book, books):
    """Collapse known duplicate editions to the strongest existing book page."""
    title = clean_title(book).lower()
    if "large language models" in title:
        for candidate in books:
            if candidate.get("slug") == "large-language-models" and is_indexable(candidate):
                return "large-language-models"
    return book["slug"]

def description(book):
    title = clean_title(book) or "This Amazon edition"
    genre = (book.get("genre") or "book").replace("-", " ")
    if book.get("description") and is_indexable(book):
        return book["description"].strip()
    if not is_indexable(book):
        return f"Amazon edition {book.get('asin','')} for the Jagdish Krishanlal Arora book catalog."
    return f"{title} by Jagdish Krishanlal Arora is a {genre} title. Explore the book details and Amazon edition on the official author website."

def page(book, canonical=None):
    indexable = is_indexable(book)
    title = clean_title(book) or f"Amazon edition {book.get('asin','')}"
    slug = book["slug"]
    desc = description(book)
    genre = (book.get("genre") or "Book").replace("-", " ").title()
    isbn = book.get("isbn")
    cover = book.get("cover")
    amazon = book.get("amazon_url") or f"https://www.amazon.com/dp/{book.get('asin','')}"
    google = book.get("google_books_url")
    canonical_slug_value = canonical or slug
    canonical_url = f"{BASE}/books/{canonical_slug_value}/"
    meta = []
    if isbn:
        meta.append(f"ISBN: {esc(isbn)}")
    if book.get("asin"):
        meta.append(f"ASIN: {esc(book['asin'])}")
    if book.get("publishedDate"):
        meta.append(f"Published: {esc(book['publishedDate'])}")
    meta_text = " · ".join(meta)
    cover_html = f'<img src="{esc(cover)}" alt="{esc(title)} cover" loading="lazy">' if cover and indexable else '<div class="book-placeholder" aria-hidden="true">BOOK</div>'
    google_link = f'<a class="button secondary" href="{esc(google)}" target="_blank" rel="noopener">Google Books ↗</a>' if google and indexable else ""
    robots = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" if indexable else "noindex, follow"
    schema = ""
    if indexable:
        schema = f'<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Book","name":title,"author":{"@type":"Person","name":"Jagdish Krishanlal Arora","url":f"{BASE}/author/"},"url":canonical_url,"isbn":isbn,"description":desc}, ensure_ascii=False)}</script>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f5f1e8">
<meta name="description" content="{esc(desc[:300])}">
<meta name="author" content="Jagdish Krishanlal Arora">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(canonical_url)}">
<meta property="og:type" content="{'book' if indexable else 'website'}">
<meta property="og:title" content="{esc(title)} by Jagdish Krishanlal Arora">
<meta property="og:description" content="{esc(desc[:300])}">
<meta property="og:url" content="{esc(canonical_url)}">
<meta property="og:site_name" content="Jagdish Krishanlal Arora">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)} by Jagdish Krishanlal Arora">
<meta name="twitter:description" content="{esc(desc[:300])}">
<meta name="twitter:image" content="{BASE}/og-image.png">
<title>{esc(title)} by Jagdish Krishanlal Arora</title>
<link rel="stylesheet" href="../../style.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{schema}
<script data-goatcounter="https://jagdishkarora.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body>
<header class="nav"><a class="brand" href="../../"><span class="brand-mark">JK</span><span>Jagdish Arora</span></a><nav><a href="../../">Home</a><a href="../">Books</a><a href="../../ai-data-experience/">AI & Data</a><a href="../../about/">About</a><a href="../../contact/">Contact</a></nav><a class="nav-cta" href="https://www.amazon.com/author/jagdisharora" target="_blank" rel="noreferrer">Amazon Author Page ↗</a></header>
<main class="section seo-page book-detail">
<section class="book-detail-hero">
{cover_html}
<div class="book-detail-copy">
<p class="eyebrow">{esc(genre)}</p>
<h1>{esc(title)}</h1>
<p class="lede">{esc(desc)}</p>
<p class="book-meta">{meta_text}</p>
<p><a class="button primary" href="{esc(amazon)}" target="_blank" rel="noopener">View on Amazon ↗</a> {google_link}</p>
</div>
</section>
<section class="prose">
<h2>{'About this book' if indexable else 'Edition reference'}</h2>
<p>{esc(desc)}</p>
<p>This page is part of the official book catalog of Jagdish Krishanlal Arora.</p>
<h2>Edition details</h2>
<ul>
<li><strong>Author:</strong> Jagdish Krishanlal Arora</li>
{f'<li><strong>{meta_text}</strong></li>' if meta_text else ''}
<li><strong>Amazon:</strong> <a href="{esc(amazon)}" target="_blank" rel="noopener">{esc(amazon)}</a></li>
</ul>
</section>
<section class="related-content"><p class="eyebrow">KEEP EXPLORING</p><h2>More books</h2><div class="related-links"><a href="../">Browse all books →</a><a href="../../author/">About the Author →</a><a href="{esc(amazon)}" target="_blank" rel="noopener">Amazon edition ↗</a></div></section>
</main>
<footer class="footer"><span>© <span id="year"></span> Jagdish Krishanlal Arora</span><span><a href="../../">Official author website</a></span></footer>
<script src="../../script.js"></script>
</body>
</html>
'''

def update_sitemap(indexable_slugs):
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    kept = []
    for line in text.splitlines():
        if "https://techbaggg.github.io/books/" in line:
            match = re.search(r"https://techbaggg\.github\.io/books/([^/<]+)/", line)
            if match:
                slug = match.group(1)
                if slug.startswith("amazon-com") and slug not in indexable_slugs:
                    continue
        kept.append(line)
    text = "\n".join(kept) + "\n"
    for slug in sorted(indexable_slugs):
        url = f"{BASE}/books/{slug}/"
        if url not in text:
            entry = f'  <url><loc>{url}</loc><lastmod>2026-09-28</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>'
            text = text.replace("</urlset>", entry + "\n</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")

payload = json.loads(DATA.read_text(encoding="utf-8"))
books = payload.get("books", [])
used = set()

for p in BOOKS.iterdir():
    if p.is_dir():
        used.add(p.name)

for book in books:
    requested = slugify(book.get("slug") or book.get("title") or "book")
    if requested in used and not (BOOKS / requested / "index.html").exists():
        used.remove(requested)
    if requested not in used:
        used.add(requested)
    book["slug"] = requested

indexable_slugs = set()
for book in books:
    canonical = canonical_slug(book, books)
    target = BOOKS / book["slug"] / "index.html"
    desired = page(book, canonical=canonical)
    if is_indexable(book):
        indexable_slugs.add(canonical)
    if not target.exists() or target.read_text(encoding="utf-8") != desired:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(desired, encoding="utf-8")

payload["books"] = books
DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
update_sitemap(indexable_slugs)
print(f"Catalog: {len(books)} records; indexable book pages: {len(indexable_slugs)}.")
