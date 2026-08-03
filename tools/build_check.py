#!/usr/bin/env python3
"""
Build gate: does the site actually build, and does every post render?

validate_post.py checks markdown in isolation. It cannot catch:
  - frontmatter that is valid-looking but invalid YAML (11ty refuses to build)
  - template errors that silently render an empty body
  - internal links pointing at pages that do not exist
  - posts that produce no output file at all

This runs the real build and inspects the output.

Usage:
    python3 build_check.py --site DIR                 # DIR contains eleventy.config.js
    python3 build_check.py --site DIR --min-words 250
"""
import argparse
import os
import re
import subprocess
import sys
from html.parser import HTMLParser


class BodyText(HTMLParser):
    """Extract visible body text and internal hrefs."""

    def __init__(self):
        super().__init__()
        self.text, self.links, self._skip, self._in_body = [], [], 0, False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._in_body = True
        if tag in ("script", "style", "nav", "footer"):
            self._skip += 1
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v and v.startswith("/"):
                    self.links.append(v)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer") and self._skip:
            self._skip -= 1

    def handle_data(self, d):
        if self._in_body and not self._skip:
            self.text.append(d)

    def words(self):
        return len(re.findall(r"\w+", " ".join(self.text)))


def build(site):
    r = subprocess.run(
        ["npx", "@11ty/eleventy"], cwd=site, capture_output=True, text=True
    )
    out = r.stdout + r.stderr
    ok = r.returncode == 0 and "Wrote 0 files" not in out
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True, help="dir containing eleventy.config.js")
    ap.add_argument("--content", default="content")
    ap.add_argument("--output", default="_site")
    ap.add_argument("--min-words", type=int, default=200)
    args = ap.parse_args()

    site = os.path.abspath(args.site)
    content = os.path.join(site, args.content)
    outdir = os.path.join(site, args.output)

    print("building ...")
    ok, log = build(site)
    if not ok:
        print("\nBUILD FAILED\n")
        for line in log.splitlines():
            if re.search(r"error|Error|trouble|line \d+", line):
                print("  " + line.strip()[:160])
        sys.exit(1)
    wrote = re.search(r"Wrote (\d+) files", log)
    print(f"build OK - {wrote.group(1) if wrote else '?'} files\n")

    errors, warnings = [], []

    # every source post must produce an output page
    sources = [f for f in os.listdir(content) if f.endswith(".md")]
    pages = {}
    for root, _dirs, files in os.walk(outdir):
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(root, f)
                pages["/" + os.path.relpath(p, outdir).replace(os.sep, "/")] = p

    permalinks, types = {}, {}
    for src in sources:
        body = open(os.path.join(content, src), encoding="utf-8", errors="ignore").read()
        m = re.search(r'^permalink:\s*"?([^"\n]+)"?', body, re.M)
        if not m:
            warnings.append(f"{src}: no permalink, cannot verify output")
            continue
        link = "/" + m.group(1).strip().strip('"')
        permalinks[src] = link
        t = re.search(r"^type:\s*(\w+)", body, re.M)
        types[link] = t.group(1) if t else "app"

    for src, link in permalinks.items():
        if link not in pages:
            errors.append(f"{src}: no output at {link}")

    # Every rendered page must have real body content. Announcements and index
    # pages are legitimately short (link lists, notices), so they get a low floor
    # that still catches a page whose body rendered empty.
    EMPTY_FLOOR = 60
    thin, short = [], []
    for url, path in sorted(pages.items()):
        raw = open(path, encoding="utf-8", errors="ignore").read()
        # Redirect stubs (written by pages_extras.py for legacy URLs) are
        # deliberately tiny - a meta refresh and one sentence.
        if 'http-equiv="refresh"' in raw:
            continue
        # 404 page is a short notice by design
        if url.endswith("/404.html"):
            continue
        parser = BodyText()
        parser.feed(raw)
        n = parser.words()
        ptype = types.get(url, "index")
        floor = args.min_words if ptype in ("app", "science") else EMPTY_FLOOR
        if n < floor:
            thin.append((url, n, ptype))
        elif ptype not in ("app", "science") and n < args.min_words:
            short.append((url, n, ptype))

    # internal links must resolve
    def resolves(href):
        href = href.split("#")[0].split("?")[0]
        if not href or not href.startswith("/"):
            return True
        if re.search(r"\.\w{2,4}$", href):  # asset
            return os.path.exists(os.path.join(outdir, href.lstrip("/")))
        cand = href.rstrip("/") + "/index.html"
        return cand in pages or href in pages

    broken = []
    for url, path in sorted(pages.items()):
        raw = open(path, encoding="utf-8", errors="ignore").read()
        parser = BodyText()
        parser.feed(raw)
        for href in set(parser.links):
            if not resolves(href):
                broken.append((url, href))

    for url, n, ptype in thin:
        errors.append(
            f"{url}: only {n} words of body text [{ptype}] - template likely rendered empty"
        )
    for url, n, ptype in short:
        warnings.append(
            f"{url}: {n} words [{ptype}] - short page, fine for a notice or index, "
            "thin if it is meant to rank"
        )
    for url, href in broken:
        errors.append(f"{url}: internal link 404 -> {href}")

    print(f"{len(sources)} source posts, {len(pages)} pages built")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print("  [warn ] " + w)
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print("  [ERROR] " + e)
        sys.exit(1)
    print("\nAll pages render with content and all internal links resolve.")


if __name__ == "__main__":
    main()
