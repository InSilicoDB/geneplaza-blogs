#!/usr/bin/env python3
"""
Harvest the WordPress taxonomy (categories + tags) that Google indexed, from the
Wayback Machine snapshots of the pre-2024 blog.

The old blog lived at www.geneplaza.com/blog/{lang}/ (and blog.geneplaza.com) and
exposed /category/{slug}/ and /tag/{slug}/ archives. The 11ty rebuild dropped them,
so those URLs now 404. This reconstructs, per taxonomy URL, which posts were in it.

Two sources of truth in a single fetch per archive page:

  1. the entry-title links     -> which posts the archive listed
  2. the <article class="...">  -> `category-x tag-y tag-z` for each listed post,
     i.e. that post's *complete* taxonomy, even for terms whose own archive page
     was never crawled by Wayback

Output JSON:
{
  "generated": "...",
  "terms":  { "/blog/en/tag/admixture/": {"kind":"tag","lang":"en","slug":"admixture",
                                          "title":"Admixture","members":["k14-...", ...],
                                          "snapshot":"2019..."} },
  "posts":  { "/blog/en/k14-ancient-cultures-admixture/": {"lang":"en",
                                          "categories":[...], "tags":[...]} }
}

Usage:
    python3 tools/wayback_taxonomy.py --out site/content/_data/legacy_taxonomy.json
    python3 tools/wayback_taxonomy.py --report          # human summary, no write
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

CDX = "http://web.archive.org/cdx/search/cdx"
HOSTS = ("geneplaza.com", "blog.geneplaza.com")
UA = "geneplaza-blog-migration/1.0 (taxonomy recovery; contact: blog@geneplaza.com)"
CACHE = ".wayback-cache"

TERM_RE = re.compile(r"/blog/(?P<lang>[a-z]{2})/(?P<kind>category|tag)/(?P<slug>[^/]+)/")
PAGE_RE = re.compile(r"/page/\d+/?$")
ARTICLE_RE = re.compile(r"<article[^>]*\bclass=\"([^\"]*)\"", re.I)
TITLE_LINK_RE = re.compile(
    r"<h[1-6][^>]*class=\"[^\"]*entry-title[^\"]*\"[^>]*>\s*<a[^>]+href=\"([^\"]+)\"", re.I
)
DOC_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
POST_URL_RE = re.compile(r"/blog/(?P<lang>[a-z]{2})/(?P<slug>[^/?#]+)/?$")


def fetch(url: str, cache_dir: str, tries: int = 3, pause: float = 1.5) -> str:
    """GET with an on-disk cache; Wayback is slow and rate-limits."""
    os.makedirs(cache_dir, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9]+", "_", url)[:180] + ".gz"
    path = os.path.join(cache_dir, key)
    if os.path.exists(path):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read().decode("utf-8", "replace")
            with gzip.open(path, "wt", encoding="utf-8") as fh:
                fh.write(body)
            time.sleep(pause)
            return body
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            time.sleep(pause * (attempt + 2))
    print(f"  ! fetch failed: {url} ({last})", file=sys.stderr)
    return ""


def cdx_taxonomy(cache_dir: str) -> dict[str, str]:
    """{canonical /blog/... path: best snapshot timestamp} for every archived term page."""
    found: dict[str, str] = {}
    for host in HOSTS:
        url = (
            f"{CDX}?url={host}&matchType=domain&output=text"
            f"&fl=original,timestamp,statuscode&collapse=urlkey"
            f"&filter=statuscode:200&filter=original:.*/(category|tag)/.*&limit=5000"
        )
        for line in fetch(url, cache_dir).splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            original, ts = parts[0], parts[1]
            m = TERM_RE.search(original)
            if not m:
                continue
            path = original.split(host, 1)[-1]
            # /page/2/ is the same term; keep it, we merge members later
            found.setdefault(path, ts)
            if ts > found[path]:  # prefer the latest capture
                found[path] = ts
    return dict(sorted(found.items()))


def parse_archive(body: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """-> (archive title, [(post url, [taxonomy classes])]) for the main loop only."""
    title = ""
    m = DOC_TITLE_RE.search(body)
    if m:
        title = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
        title = re.sub(r"\s*(Archives?|Archief|Archieven)\s*[-–—|].*$", "", title).strip()

    out: list[tuple[str, list[str]]] = []
    # Walk <article> blocks: sidebar "recent posts" widgets are <li>, not <article>,
    # so this keeps us inside the real loop.
    chunks = re.split(r"(?=<article)", body)
    for chunk in chunks[1:]:
        cls = ARTICLE_RE.match(chunk)
        link = TITLE_LINK_RE.search(chunk)
        if not (cls and link):
            continue
        terms = [c for c in cls.group(1).split() if c.startswith(("category-", "tag-"))]
        out.append((html.unescape(link.group(1)), terms))
    return title, out


def post_path(url: str) -> str | None:
    m = POST_URL_RE.search(url.split("?")[0])
    if not m:
        return None
    slug = m.group("slug")
    if slug in {"feed", "page", "category", "tag", "author"}:
        return None
    return f"/blog/{m.group('lang')}/{slug}/"


def harvest(cache_dir: str) -> dict:
    index = cdx_taxonomy(cache_dir)
    print(f"CDX: {len(index)} archived taxonomy URLs", file=sys.stderr)

    terms: dict[str, dict] = {}
    posts: dict[str, dict] = {}

    for path, ts in index.items():
        canonical = PAGE_RE.sub("/", path)
        m = TERM_RE.search(canonical)
        if not m:
            continue
        snap = f"http://web.archive.org/web/{ts}id_/https://www.geneplaza.com{path}"
        body = fetch(snap, cache_dir)
        if not body:
            continue
        title, entries = parse_archive(body)
        rec = terms.setdefault(
            canonical,
            {
                "kind": m.group("kind"),
                "lang": m.group("lang"),
                "slug": m.group("slug"),
                "title": title,
                "members": [],
                "snapshot": ts,
                "paged": [],
            },
        )
        if path != canonical:
            rec["paged"].append(path)
        for url, classes in entries:
            p = post_path(url)
            if not p:
                continue
            if p not in rec["members"]:
                rec["members"].append(p)
            pm = POST_URL_RE.search(p)
            prec = posts.setdefault(
                p, {"lang": pm.group("lang"), "categories": [], "tags": []}
            )
            for c in classes:
                bucket, term = (
                    ("categories", c[len("category-"):])
                    if c.startswith("category-")
                    else ("tags", c[len("tag-"):])
                )
                if term not in prec[bucket]:
                    prec[bucket].append(term)
        print(f"  {canonical:52s} {len(rec['members']):2d} posts", file=sys.stderr)

    for rec in terms.values():
        rec["members"].sort()
        rec["paged"].sort()
    return {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": "web.archive.org",
        "terms": dict(sorted(terms.items())),
        "posts": dict(sorted(posts.items())),
    }


def report(data: dict) -> None:
    terms = data["terms"]
    print(f"\n{len(terms)} taxonomy terms, {len(data['posts'])} distinct legacy posts\n")
    rows = sorted(terms.items(), key=lambda kv: (-len(kv[1]["members"]), kv[0]))
    print(f"{'legacy URL':52s} {'kind':9s} {'posts':>5s}  title")
    print("-" * 96)
    for path, rec in rows:
        print(f"{path:52s} {rec['kind']:9s} {len(rec['members']):5d}  {rec['title'][:30]}")
    counts = [len(r["members"]) for r in terms.values()]
    for n in (0, 1, 2, 3):
        k = sum(1 for c in counts if (c == n if n < 3 else c >= 3))
        label = f">={n}" if n == 3 else f"=={n}"
        print(f"terms with {label:>3s} posts: {k}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write JSON here")
    ap.add_argument("--cache-dir", default=CACHE)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    data = harvest(args.cache_dir)
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\nwrote {args.out}", file=sys.stderr)
    if args.report or not args.out:
        report(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
