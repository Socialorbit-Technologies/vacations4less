#!/usr/bin/env python3
"""Build the Vacations4Less static site.

- src/pages/*.html  -> public/<name>.html          (main pages)
- src/blog/*.html   -> public/blog/<slug>/index.html (one per post)
- blog index        -> public/blog/index.html       (generated)
- sitemap.xml, robots.txt, assets, contact.php, .htaccess

Every source file starts with a <!--meta {...} --> JSON block.
Use {{base}} for internal links so nested pages resolve correctly,
and {{blog_latest}} on any page to drop in the latest-posts list.

Usage:
  python3 build.py                 # staging build (noindex)
  STAGING=0 python3 build.py       # production build (indexable)
"""
import html as htmlmod
import json
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

SITE_URL = os.environ.get("SITE_URL", "https://vacations4less.us/").rstrip("/") + "/"
STAGING = os.environ.get("STAGING", "1") != "0"
VERSION = time.strftime("%Y%m%d%H%M")
ROOT_PATH = os.environ.get("ROOT_PATH", "/staging/" if STAGING else "/")
UPLOADS = "https://vacations4less.us/wp-content/uploads/"
DEFAULT_OG = UPLOADS + "2023/03/White-wash-staircases-on-Santorini-Island-Greece.-The-view-toward-Caldera-sea-with-cruise-ship-awaiting.-1536x1026.jpeg"

META_RE = re.compile(r"^\s*<!--meta\s+(\{.*?\})\s*-->\s*", re.S)

ORG = {
    "@type": "TravelAgency",
    "@id": SITE_URL + "#agency",
    "name": "Vacations4Less",
    "url": SITE_URL,
    "telephone": "+1-808-232-9000",
    "email": "contact@vacations4less.us",
    "logo": SITE_URL + "assets/img/mark.svg",
    "image": DEFAULT_OG,
    "description": "Independent IATAN and CLIA accredited travel agency booking hotels, flights, rental cars, cruises and activities worldwide.",
    "areaServed": "Worldwide",
    "memberOf": [
        {"@type": "Organization", "name": "International Airlines Travel Agent Network (IATAN)"},
        {"@type": "Organization", "name": "Cruise Lines International Association (CLIA)"},
    ],
}


def read_source(path):
    raw = path.read_text()
    m = META_RE.match(raw)
    if not m:
        raise SystemExit(f"{path}: missing <!--meta {{...}} --> block")
    return json.loads(m.group(1)), raw[m.end():]


def nice_date(iso):
    d = datetime.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def ld(obj):
    obj = dict(obj)
    obj.setdefault("@context", "https://schema.org")
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def render(header, footer, body, *, meta, out_path, base, extra_schema=""):
    noindex = STAGING or meta.get("noindex")
    nav = meta.get("nav", "")
    values = {
        "title": htmlmod.escape(meta["title"]),
        "description": htmlmod.escape(meta["description"]),
        "canonical": SITE_URL + meta.get("path", ""),
        "og_image": meta.get("og_image", DEFAULT_OG),
        "og_type": meta.get("og_type", "website"),
        "robots": '<meta name="robots" content="noindex, nofollow">' if noindex else
                  '<meta name="robots" content="index, follow, max-image-preview:large">',
        "schema": extra_schema,
        "version": VERSION,
    }
    for key in ("home", "services", "about", "blog", "contact"):
        values[f"nav_{key}"] = 'aria-current="page"' if nav == key else ""

    html = header + body + footer
    for k, v in values.items():
        html = html.replace("{{" + k + "}}", v)
    html = html.replace("{{base}}", base)
    leftover = re.findall(r"\{\{\w+\}\}", html)
    if leftover:
        raise SystemExit(f"{out_path}: unfilled placeholders {sorted(set(leftover))}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    print("built", out_path.relative_to(OUT))


def post_card(p, base, heading="h3"):
    return f"""<article class="post-card">
  <a class="post-card-photo" href="{base}blog/{p['slug']}/" tabindex="-1" aria-hidden="true"><img src="{UPLOADS}{p['thumb']}" alt="" loading="lazy" width="768" height="432"></a>
  <div class="post-card-body">
    <p class="post-meta"><span class="post-cat">{htmlmod.escape(p['category'])}</span> <time datetime="{p['date'][:10]}">{nice_date(p['date'])}</time></p>
    <{heading}><a href="{base}blog/{p['slug']}/">{htmlmod.escape(p['title'])}</a></{heading}>
    <p>{htmlmod.escape(p['excerpt'])}</p>
  </div>
</article>"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    header = (SRC / "partials/header.html").read_text()
    footer = (SRC / "partials/footer.html").read_text()
    sitemap = []

    # ---- Blog posts -------------------------------------------------------
    posts = []
    for f in sorted((SRC / "blog").glob("*.html")):
        meta, body = read_source(f)
        meta["slug"] = f.stem
        meta["body"] = body
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)

    post_tpl = (SRC / "partials/post.html").read_text()
    for i, p in enumerate(posts):
        base = "../../"
        others = [q for q in posts if q is not p][:2]
        more = "".join(post_card(q, base) for q in others)
        body = post_tpl
        repl = {
            "post_title": htmlmod.escape(p["title"]),
            "post_category": htmlmod.escape(p["category"]),
            "post_date_iso": p["date"][:10],
            "post_date": nice_date(p["date"]),
            "post_cover": UPLOADS + p["cover"],
            "post_cover_alt": htmlmod.escape(p["cover_alt"]),
            "post_body": p["body"],
            "post_more": more or '<p>More travel tips are on the way.</p>',
        }
        for k, v in repl.items():
            body = body.replace("{{" + k + "}}", v)
        path = f"blog/{p['slug']}/"
        schema = ld({
            "@type": "BlogPosting",
            "headline": p["title"],
            "description": p["description"],
            "datePublished": p["date"],
            "dateModified": p.get("modified", p["date"]),
            "image": UPLOADS + p["cover"],
            "mainEntityOfPage": SITE_URL + path,
            "author": {"@id": SITE_URL + "#agency", "@type": "TravelAgency", "name": "Vacations4Less"},
            "publisher": {"@id": SITE_URL + "#agency", "@type": "TravelAgency", "name": "Vacations4Less"},
        }) + ld({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Travel tips", "item": SITE_URL + "blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": SITE_URL + path},
            ],
        })
        render(header, footer, body,
               meta={"title": p["seo_title"], "description": p["description"], "path": path,
                     "nav": "blog", "og_image": UPLOADS + p["cover"], "og_type": "article"},
               out_path=OUT / path / "index.html", base=base, extra_schema=schema)
        sitemap.append((path, p.get("modified", p["date"])[:10]))

    # ---- Blog index -------------------------------------------------------
    meta, body = read_source(SRC / "blog-index.html")
    body = body.replace("{{post_list}}", "\n".join(post_card(p, "../", "h2") for p in posts))
    render(header, footer, body, meta=meta, out_path=OUT / "blog/index.html", base="../")
    sitemap.append(("blog/", posts[0]["date"][:10] if posts else None))

    # ---- Main pages -------------------------------------------------------
    home_posts = sorted(posts, key=lambda p: not p.get("pin"))[:3]
    latest = "\n".join(post_card(p, "") for p in home_posts)
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = read_source(page)
        body = body.replace("{{blog_latest}}", latest)
        schema = ""
        if meta.get("schema"):
            schema = ld(ORG)
        faq = re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<div>(.*?)</div>', body, re.S)
        if faq:
            schema += ld({
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": re.sub(r"<[^>]+>", "", q).strip(),
                     "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", a)).strip()}}
                    for q, a in faq
                ],
            })
        render(header, footer, body, meta=meta, out_path=OUT / page.name, base="", extra_schema=schema)
        if not meta.get("noindex"):
            sitemap.append((meta.get("path", ""), None))

    # ---- Static files -----------------------------------------------------
    shutil.copytree(SRC / "assets", OUT / "assets")
    shutil.copy2(SRC / "contact.php", OUT / "contact.php")
    ht = (SRC / ".htaccess").read_text()
    if not STAGING:
        ht = re.sub(r"# STAGING ONLY.*?# END STAGING ONLY\n", "", ht, flags=re.S)
    (OUT / ".htaccess").write_text(ht.replace("{{root}}", ROOT_PATH))

    today = time.strftime("%Y-%m-%d")
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{d or today}</lastmod></url>" for p, d in sitemap
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n"
    )
    robots = "User-agent: *\nDisallow: /\n" if STAGING else f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots)
    print(f"done -> {OUT}  (staging={STAGING}, posts={len(posts)})")


if __name__ == "__main__":
    build()
