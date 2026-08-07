#!/usr/bin/env python3
"""Copy a Reddit answer to the clipboard, ready to paste."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "reddit-answers.md")
BLOG = "https://www.geneplaza.com/blog"

ANSWERS = [
    ("Why did my ancestry percentages change?",
     f"{BLOG}/en/what-is-genetic-ancestry/", "r/AncestryDNA, r/23andMe",
     "ancestry percentages changed"),
    ("I have the MTHFR mutation — should I be worried?",
     f"{BLOG}/en/mthfr-testing-acmg/", "r/23andMe, r/genetics", "MTHFR"),
    ("Is the cilantro-soap gene real?",
     f"{BLOG}/en/cilantro-tastes-like-soap-genetics/", "r/23andMe", "cilantro soap"),
    ("My report says increased risk — should I worry?",
     f"{BLOG}/en/childhood-inflammation-depression-risk/", "r/23andMe, r/genetics",
     "increased risk depression"),
    ("What does K12/K29/K36 mean?",
     f"{BLOG}/en/how-to-read-admixture-bar-charts/", "r/AncestryDNA, r/genealogy",
     "admixture calculator K"),
    ("Am I descended from Cheddar Man?",
     f"{BLOG}/en/cheddar-man-dark-skin-blue-eyes/", "r/genealogy, r/AskHistorians",
     "Cheddar Man"),
]

DISCLOSURE = ("(Disclosure: I'm a co-founder at GenePlaza, so treat the link as "
              "context rather than a recommendation — the papers are the point.)")


def section(n):
    """Extract the body of '## n. ...' up to the next horizontal rule."""
    text = open(SRC, encoding="utf-8").read()
    m = re.search(rf"^## {n}\..*?$(.*?)^---$", text, re.S | re.M)
    if not m:
        sys.exit(f"section {n} not found in {SRC}")
    body = m.group(1)
    body = re.sub(r"^\*\*Highest-value.*?\n", "", body, flags=re.M)   # editorial note
    body = re.sub(r"^> ?", "", body, flags=re.M)                      # unquote
    body = re.sub(r"\n{3,}", "\n\n", body)                            # squeeze blanks
    return body.strip()


def main():
    if len(sys.argv) == 1:
        print("Reddit answers — ./tools/rcopy.sh <n> [--link]\n")
        for i, (title, _l, subs, _q) in enumerate(ANSWERS, 1):
            print(f"  {i}  {title:<48} {subs}")
        print("\nWeeks 1-2: omit --link. Answer only.")
        print("Find live threads:")
        for i, (_t, _l, subs, q) in enumerate(ANSWERS, 1):
            sub = subs.split(",")[0].strip().replace("r/", "")
            url = ("https://www.reddit.com/r/" + sub + "/search/?q=" +
                   q.replace(" ", "+") + "&restrict_sr=1&sort=new")
            print(f"  {i}  {url}")
        return

    n = int(sys.argv[1])
    if not 1 <= n <= len(ANSWERS):
        sys.exit(f"no answer {n}")
    title, link, subs, query = ANSWERS[n - 1]

    body = section(n)
    with_link = "--link" in sys.argv
    if with_link:
        body += f"\n\nMore detail and the papers here: {link}\n\n{DISCLOSURE}"

    subprocess.run(["pbcopy"], input=body, text=True, check=True)

    print(f"copied answer {n} — {title}")
    print(f"subs: {subs}")
    print("link INCLUDED (week 3+)" if with_link else "no link (weeks 1-2)")
    sub = subs.split(",")[0].strip().replace("r/", "")
    print("find threads: https://www.reddit.com/r/" + sub + "/search/?q=" +
          query.replace(" ", "+") + "&restrict_sr=1&sort=new")
    print(f"\n{len(body)} characters on the clipboard\n--- preview ---")
    print("\n".join(body.splitlines()[:10]))
    print("...")


if __name__ == "__main__":
    main()
