#!/usr/bin/env python3
"""Generate individual SEO-friendly book pages from data/books.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.json"
BOOKS = ROOT / "books"
SITEMAP = ROOT / "sitemap.xml"

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

def description(book):
    title = book.get("title") or "This book"
    genre = (book.get("genre") or "book").replace("-", " ")
    if book.get("description"):
        return book["description"].strip()
    return f"{title} by Jagdish Krishanlal Arora is a {genre} title. Explore the book details, edition information and the Amazon listing on the official author website."

def page(book):
    title = book.get("title") or f"Amazon Edition {book.get('asin','')}"
    slug = book["slug"]
    desc = description(book)
    genre = (book.get("genre") or "Book").replace("-", " ").title()
    isbn = book.get("isbn")
    cover = book.get("cover")
    amazon = book.get("amazon_url") or f"https://www.amazon.com/dp/{book.get('asin','')}"
    google = book.get("google_books_url")
    meta = []
    if isbn: meta.append(f"ISBN: {esc(isbn)}")
    if book.get("asin"): meta.append(f"ASIN: {esc(book['asin'])}")
    if book.get("publishedDate"): meta.append(f"Published: {esc(book['publishedDate'])}")
    meta_text = " · ".join(meta)
    cover_html = f'<img src="{esc(cover)}" alt="{esc(title)} cover" loading="lazy">' if cover else '<div class="book-placeholder" aria-hidden="true">BOOK</div>'
    google_link = f'<a class="button secondary" href="{esc(google)}" target="_blank" rel="noopener">Google Books ↗</a>' if google else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f5f1e8">
<meta name="description" content="{esc(desc[:300])}">
<meta name="author" content="Jagdish Krishanlal Arora">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="https://techbaggg.github.io/books/{esc(slug)}/">
<meta property="og:type" content="book">
<meta property="og:title" content="{esc(title)} by Jagdish Krishanlal Arora">
<meta property="og:description" content="{esc(desc[:300])}">
<meta property="og:url" content="https://techbaggg.github.io/books/{esc(slug)}/">
<meta property="og:site_name" content="Jagdish Krishanlal Arora">
<meta property="og:image" content="https://techbaggg.github.io/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)} by Jagdish Krishanlal Arora">
<meta name="twitter:description" content="{esc(desc[:300])}">
<meta name="twitter:image" content="https://techbaggg.github.io/og-image.png">
<title>{esc(title)} by Jagdish Krishanlal Arora</title>
<link rel="stylesheet" href="../../style.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Book","name":title,"author":{"@type":"Person","name":"Jagdish Krishanlal Arora","url":"https://techbaggg.github.io/author/"},"url":f"https://techbaggg.github.io/books/{slug}/","isbn":isbn,"description":desc}, ensure_ascii=False)}</script>
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
<h2>About this book</h2>
<p>{esc(desc)}</p>
<p>This page is part of the official book catalog of Jagdish Krishanlal Arora. Edition identifiers are included where available so readers can distinguish between different Amazon editions.</p>
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

def update_sitemap(slugs):
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    for slug in slugs:
        url = f"https://techbaggg.github.io/books/{slug}/"
        if url not in text:
            entry = f"  <url><loc>{url}</loc></url>\n"
            text = text.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")

payload = json.loads(DATA.read_text(encoding="utf-8"))
books = payload.get("books", [])
used = set()
generated = []

# Existing directory names are treated as reserved URLs.
for p in BOOKS.iterdir():
    if p.is_dir():
        used.add(p.name)

# Preserve existing slugs when they already have a directory; assign unique slugs to duplicates.
for book in books:
    requested = slugify(book.get("slug") or book.get("title") or "book")
    if requested in used:
        # Existing page is kept as the canonical page for the first matching record.
        if book.get("slug") == requested and not (BOOKS / requested / "index.html").exists():
            pass
        elif (BOOKS / requested / "index.html").exists():
            # Existing page is reserved; duplicate editions get an ASIN-specific URL.
            if any(b is not book and b.get("slug") == requested for b in books):
                requested = f"{requested}-{book.get('asin','').lower()}"
                n = 2
                while requested in used:
                    requested = f"{slugify(book.get('title'))}-{book.get('asin','').lower()}-{n}"
                    n += 1
    if requested not in used:
        used.add(requested)
    book["slug"] = requested
    target = BOOKS / requested / "index.html"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(book), encoding="utf-8")
        generated.append(requested)

payload["books"] = books
DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
update_sitemap({b["slug"] for b in books})
print(f"Generated {len(generated)} new book pages.")
