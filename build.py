#!/usr/bin/env python3
"""Build the Vacations4Less static site.

Assembles src/pages/*.html with the shared header/footer partials into public/,
and copies assets, contact.php and .htaccess.

Usage:
  python3 build.py                 # staging build (noindex, canonical -> live domain)
  STAGING=0 python3 build.py       # production build (indexable)
"""
import html as htmlmod
import json
import os
import re
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

SITE_URL = os.environ.get("SITE_URL", "https://vacations4less.us/").rstrip("/") + "/"
STAGING = os.environ.get("STAGING", "1") != "0"
VERSION = time.strftime("%Y%m%d%H%M")

META_RE = re.compile(r"^\s*<!--meta\s+(\{.*?\})\s*-->\s*", re.S)

SCHEMA = {
    "@context": "https://schema.org",
    "@type": "TravelAgency",
    "name": "Vacations4Less",
    "url": SITE_URL,
    "telephone": "+1-808-232-9000",
    "email": "contact@vacations4less.us",
    "logo": SITE_URL + "assets/img/mark.svg",
    "description": "Independent IATAN and CLIA accredited travel agency booking hotels, flights, rental cars, cruises and activities.",
    "memberOf": [
        {"@type": "Organization", "name": "International Airlines Travel Agent Network (IATAN)"},
        {"@type": "Organization", "name": "Cruise Lines International Association (CLIA)"},
    ],
}


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    header = (SRC / "partials/header.html").read_text()
    footer = (SRC / "partials/footer.html").read_text()

    for page in sorted((SRC / "pages").glob("*.html")):
        raw = page.read_text()
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"{page.name}: missing <!--meta {{...}} --> block")
        meta = json.loads(m.group(1))
        body = raw[m.end():]

        noindex = STAGING or meta.get("noindex")
        nav = meta.get("nav", "")
        values = {
            "title": htmlmod.escape(meta["title"]),
            "description": htmlmod.escape(meta["description"]),
            "canonical": SITE_URL + meta.get("path", ""),
            "robots": '<meta name="robots" content="noindex, nofollow">' if noindex else
                      '<meta name="robots" content="index, follow, max-image-preview:large">',
            "schema": ('<script type="application/ld+json">' + json.dumps(SCHEMA) + "</script>")
                      if meta.get("schema") else "",
            "version": VERSION,
        }
        for key in ("home", "services", "about", "contact"):
            values[f"nav_{key}"] = 'aria-current="page"' if nav == key else ""

        html = header + body + footer
        for k, v in values.items():
            html = html.replace("{{" + k + "}}", v)
        leftover = re.findall(r"\{\{\w+\}\}", html)
        if leftover:
            raise SystemExit(f"{page.name}: unfilled placeholders {leftover}")
        (OUT / page.name).write_text(html)
        print("built", page.name)

    shutil.copytree(SRC / "assets", OUT / "assets")
    shutil.copy2(SRC / "contact.php", OUT / "contact.php")
    shutil.copy2(SRC / ".htaccess", OUT / ".htaccess")
    if not STAGING:
        # Drop the staging-only noindex header for production
        ht = (OUT / ".htaccess").read_text()
        ht = re.sub(r"# STAGING ONLY.*?</IfModule>\n", "", ht, flags=re.S)
        (OUT / ".htaccess").write_text(ht)
    print(f"done -> {OUT}  (staging={STAGING})")


if __name__ == "__main__":
    build()
