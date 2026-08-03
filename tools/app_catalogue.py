#!/usr/bin/env python3
"""
GenePlaza app catalogue - the citation spine for the blog.

Every in-store app records the study it is built on in its `developer` field.
That study is the mandatory scientific source for the post that sells the app.

Usage:
    python3 app_catalogue.py --refresh      # re-fetch from the live API
    python3 app_catalogue.py --list         # print the in-store catalogue
    python3 app_catalogue.py --app 61       # show one app in full
    python3 app_catalogue.py --unwritten    # apps with no post yet (needs --posts DIR)
"""
import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request

API = "https://consumer-api.geneplaza.com/api/apps?page[number]=1&page[size]=100"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps.json")
APP_URL = "https://www.geneplaza.com/app-store/{id}"


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    return re.sub(r"\s+", " ", text).strip()


def fetch():
    """Fetch the catalogue. Uses curl first (system CA store), falls back to urllib."""
    try:
        out = subprocess.run(
            ["curl", "-sS", "-m", "45", "-H", "Accept: application/vnd.api+json", API],
            capture_output=True, text=True, check=True,
        ).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        req = urllib.request.Request(API, headers={"Accept": "application/vnd.api+json"})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
            return json.load(r)


def refresh():
    payload = fetch()
    apps = []
    for entry in payload["data"]:
        a = entry["attributes"]
        if a.get("in-store") != 1:
            continue
        apps.append(
            {
                "id": str(entry["id"]),
                "title": a.get("title"),
                "study": a.get("developer"),
                "institution": a.get("institution"),
                "category": [c.strip() for c in re.findall(r'"([^"]+)"', a.get("category") or "")],
                "price": a.get("price"),
                "short_description": strip_html(a.get("short-description")),
                "long_description": strip_html(a.get("long-description")),
                "url": APP_URL.format(id=entry["id"]),
            }
        )
    apps.sort(key=lambda x: int(x["id"]))
    with open(CACHE, "w") as f:
        json.dump(apps, f, indent=2)
    return apps


def load():
    if not os.path.exists(CACHE):
        return refresh()
    with open(CACHE) as f:
        return json.load(f)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--list", action="store_true")
    p.add_argument("--app")
    p.add_argument("--unwritten", action="store_true")
    p.add_argument("--coverage", action="store_true",
                   help="every in-store app and the post that sells it, by cluster")
    p.add_argument("--posts", help="directory of published posts")
    args = p.parse_args()

    apps = refresh() if args.refresh else load()

    if args.refresh and not (args.list or args.app):
        print(f"Refreshed {len(apps)} in-store apps -> {CACHE}")
        return

    if args.app:
        for a in apps:
            if a["id"] == str(args.app):
                print(json.dumps(a, indent=2))
                return
        sys.exit(f"No in-store app with id {args.app}")

    if args.coverage:
        if not args.posts:
            sys.exit("--coverage requires --posts DIR")
        # app id -> [posts linking it]
        links = {a["id"]: [] for a in apps}
        for fn in sorted(os.listdir(args.posts)):
            if not fn.endswith(".md"):
                continue
            body = open(os.path.join(args.posts, fn), encoding="utf-8", errors="ignore").read()
            for aid in set(re.findall(r"app-store/(\d+)", body)):
                if aid in links:
                    links[aid].append(fn)

        def cluster(a):
            t = a["title"]
            base = re.sub(r"\s*-\s*(Beginner|Advance[d]?)$", "", t)
            base = re.sub(r"\s*(Beginner|Advanced)\s*DNA Package$", "", base)
            base = re.sub(r"\s*DNA (Test|Package)$", "", base).strip()
            return base

        by_cluster = {}
        for a in apps:
            by_cluster.setdefault(cluster(a), []).append(a)

        covered = uncovered = 0
        print(f"COVERAGE - {len(apps)} in-store apps in {len(by_cluster)} topic clusters\n")
        for name, group in sorted(by_cluster.items()):
            done = [a for a in group if links[a["id"]]]
            mark = "OK  " if len(done) == len(group) else ("PART" if done else "TODO")
            print(f"[{mark}] {name}  ({len(done)}/{len(group)} apps linked)")
            for a in group:
                ps = links[a["id"]]
                covered += bool(ps)
                uncovered += not ps
                print(f"        {a['id']:>5}  {a['title'][:44]:44} {ps[0] if ps else '-- no post --'}")
        print(f"\n{covered}/{len(apps)} apps have a post linking them; {uncovered} do not.")
        print("A collapsed cluster is fully covered when ONE post links every app id in it.")
        return

    if args.unwritten:
        if not args.posts:
            sys.exit("--unwritten requires --posts DIR")
        written = set()
        for fn in os.listdir(args.posts):
            if not fn.endswith(".md"):
                continue
            body = open(os.path.join(args.posts, fn), encoding="utf-8", errors="ignore").read()
            for m in re.findall(r"app-store/(\d+)", body):
                written.add(m)
        todo = [a for a in apps if a["id"] not in written]
        print(f"{len(todo)} of {len(apps)} in-store apps still have no post:\n")
        for a in todo:
            print(f"  {a['id']:>5}  {a['title']}")
        return

    # default: list
    print(f"{len(apps)} in-store GenePlaza apps\n")
    for a in apps:
        print(f"{a['id']:>5} | {str(a['title'])[:44]:44} | {str(a['study'])[:60]}")


if __name__ == "__main__":
    main()
