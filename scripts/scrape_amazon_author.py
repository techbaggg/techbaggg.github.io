#!/usr/bin/env python3
import json, re, sys, urllib.request
from pathlib import Path
from datetime import datetime, timezone

URL = "https://www.amazon.com/stores/Jagdish-Arora/author/B07FB9KSB6"
OUT = Path("data/amazon-discovered-books.json")

req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (compatible; JagdishAroraBookCatalog/1.0; +https://techbaggg.github.io/)"
})
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode("utf-8", "ignore")
except Exception as exc:
    print(f"Amazon author page could not be fetched: {exc}")
    print("Keeping the existing catalog unchanged.")
    sys.exit(0)

if "Robot Check" in html or "captcha" in html.lower():
    print("Amazon returned a bot/captcha page; keeping existing catalog unchanged.")
    sys.exit(0)

asins = set()
for pattern in [
    r'data-asin=["\']([A-Z0-9]{10})["\']',
    r'/dp/([A-Z0-9]{10})',
    r'/gp/product/([A-Z0-9]{10})',
]:
    asins.update(re.findall(pattern, html, re.I))

books = [{"asin": a.upper(), "amazon_url": f"https://www.amazon.com/dp/{a.upper()}"} for a in sorted(asins)]
OUT.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "source": URL,
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "count": len(books),
    "books": books,
}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Discovered {len(books)} Amazon product identifiers.")
