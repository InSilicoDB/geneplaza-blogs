#!/usr/bin/env python3
"""
Post-build extras for a GitHub Pages deploy.

GitHub Pages serves static files only - there is no server-side redirect support,
so the Netlify-style `_redirects` file does nothing there. This generates:

  1. an HTML redirect page for every rule in _redirects (meta refresh + canonical
     + JS, which is how you approximate a 301 on a static host)
  2. a CNAME file, required for a custom domain
  3. a root index that forwards / to /blog/
  4. a 404.html

Usage:
    python3 pages_extras.py --site site --domain blog.geneplaza.com
"""
import argparse
import os

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="{abs_target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="robots" content="noindex">
<script>location.replace("{target}" + location.search + location.hash);</script>
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""

NOT_FOUND = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page not found — GenePlaza Blog</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{margin:0;font-family:"Work Sans",Helvetica,Arial,sans-serif;color:#4a4a4a;
 display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center}}
div{{max-width:32rem;padding:2rem}}
h1{{color:#000;font-size:1.8rem;margin:0 0 .6rem}}
a{{color:#44355b}}
</style>
</head>
<body>
<div>
  <h1>Page not found</h1>
  <p>That address does not exist on the GenePlaza blog.</p>
  <p><a href="/blog/">Browse all posts</a> · <a href="https://www.geneplaza.com/app-store">App Store</a></p>
</div>
</body>
</html>
"""

ROOT_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GenePlaza Blog</title>
<link rel="canonical" href="https://{domain}/blog/">
<meta http-equiv="refresh" content="0; url=/blog/">
<script>location.replace("/blog/");</script>
</head>
<body><p><a href="/blog/">GenePlaza Blog</a></p></body>
</html>
"""


def parse_redirects(path):
    rules = []
    if not os.path.exists(path):
        return rules
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            rules.append((parts[0], parts[1]))
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--output", default="_site")
    args = ap.parse_args()

    out = os.path.join(args.site, args.output)
    if not os.path.isdir(out):
        raise SystemExit(f"{out} does not exist - run the build first")

    # 1. redirect pages
    rules = parse_redirects(os.path.join(args.site, "_redirects"))
    written = 0
    for src, target in rules:
        rel = src.strip("/")
        dest_dir = os.path.join(out, rel)
        dest = os.path.join(dest_dir, "index.html")
        if os.path.exists(dest):
            print(f"  skip (real page exists): /{rel}/")
            continue
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(REDIRECT_HTML.format(
                target=target, abs_target=f"https://{args.domain}{target}"))
        written += 1
    print(f"{written} redirect page(s) from {len(rules)} rule(s)")

    # 2. CNAME
    with open(os.path.join(out, "CNAME"), "w", encoding="utf-8") as f:
        f.write(args.domain + "\n")
    print(f"CNAME -> {args.domain}")

    # 3. root index
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(ROOT_INDEX.format(domain=args.domain))
    print("root index -> /blog/")

    # 4. 404
    with open(os.path.join(out, "404.html"), "w", encoding="utf-8") as f:
        f.write(NOT_FOUND)
    print("404.html written")


if __name__ == "__main__":
    main()
