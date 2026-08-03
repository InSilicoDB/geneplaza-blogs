#!/usr/bin/env python3
"""
Read Google Search Console data for geneplaza.com.

Read-only. Uses your local application-default credentials — nothing is uploaded
and no settings can be changed.

Setup (once):
    gcloud auth application-default login \\
      --scopes="https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform"

Usage:
    python3 gsc.py --sites                      # which properties are visible
    python3 gsc.py --queries --days 28          # top queries
    python3 gsc.py --pages   --days 28          # top pages
    python3 gsc.py --countries --days 28
    python3 gsc.py --coverage                   # which posts have any impressions
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import urllib.parse

API = "https://searchconsole.googleapis.com/webmasters/v3"
SITE_DEFAULT = "sc-domain:geneplaza.com"


def token():
    for cmd in (
        ["gcloud", "auth", "application-default", "print-access-token"],
        ["gcloud", "auth", "print-access-token"],
    ):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    sys.exit("No gcloud token. Run the application-default login shown in --help.")


def call(path, payload=None, tok=None):
    tok = tok or token()
    args = ["curl", "-sS", "-m", "60", f"{API}{path}",
            "-H", f"Authorization: Bearer {tok}"]
    if payload is not None:
        args += ["-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        sys.exit(f"Unexpected response: {out[:200]}")
    if isinstance(d, dict) and "error" in d:
        e = d["error"]
        msg = e.get("message", "")
        if e.get("code") == 403 and "scope" in msg.lower():
            sys.exit(
                "403: the token lacks the Search Console scope.\n"
                "Run:\n  gcloud auth application-default login "
                '--scopes="https://www.googleapis.com/auth/webmasters.readonly,'
                'https://www.googleapis.com/auth/cloud-platform"'
            )
        if e.get("code") == 403:
            sys.exit(f"403: {msg}\nIs the property verified, and does this account have access?")
        sys.exit(f"{e.get('code')}: {msg}")
    return d


def query(site, days, dims, limit=25, filters=None):
    end = dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=days)
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dims,
        "rowLimit": limit,
    }
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    enc = urllib.parse.quote(site, safe="")
    return call(f"/sites/{enc}/searchAnalytics/query", body).get("rows", [])


def table(rows, dims, title):
    print(f"\n{title}")
    if not rows:
        print("  (no data yet — new pages typically take days to weeks to appear)")
        return
    print(f"  {'key':<58} {'clicks':>7} {'impr':>8} {'ctr':>7} {'pos':>6}")
    for r in rows:
        key = " · ".join(r["keys"])[:57]
        print(f"  {key:<58} {r['clicks']:>7.0f} {r['impressions']:>8.0f}"
              f" {r['ctr']*100:>6.1f}% {r['position']:>6.1f}")
    print(f"  {'TOTAL':<58} {sum(r['clicks'] for r in rows):>7.0f}"
          f" {sum(r['impressions'] for r in rows):>8.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=SITE_DEFAULT)
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--sites", action="store_true")
    ap.add_argument("--queries", action="store_true")
    ap.add_argument("--pages", action="store_true")
    ap.add_argument("--countries", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    a = ap.parse_args()

    if a.sites or not any([a.queries, a.pages, a.countries, a.coverage]):
        d = call("/sites")
        entries = d.get("siteEntry", [])
        print(f"{len(entries)} property/properties visible to this account:")
        for e in entries:
            print(f"  {e['siteUrl']:<44} {e.get('permissionLevel')}")
        if not entries:
            print("  none — create and verify the property first")
        if not any([a.queries, a.pages, a.countries, a.coverage]):
            return

    if a.queries:
        table(query(a.site, a.days, ["query"], a.limit),
              ["query"], f"Top queries — last {a.days} days")
    if a.pages:
        table(query(a.site, a.days, ["page"], a.limit),
              ["page"], f"Top pages — last {a.days} days")
    if a.countries:
        table(query(a.site, a.days, ["country"], a.limit),
              ["country"], f"By country — last {a.days} days")
    if a.coverage:
        rows = query(a.site, a.days, ["page"], 1000)
        blog = [r for r in rows if "/blog/" in r["keys"][0]]
        print(f"\nBlog pages with any impressions in {a.days} days: {len(blog)}")
        for r in sorted(blog, key=lambda x: -x["impressions"])[:20]:
            print(f"  {r['impressions']:>6.0f} impr  {r['keys'][0]}")


if __name__ == "__main__":
    main()
