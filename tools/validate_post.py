#!/usr/bin/env python3
"""
Deterministic gate for GenePlaza blog posts.

Checks the things a machine can prove. It does NOT check whether a claim
faithfully represents its paper - that is the agent's job (see SKILL.md).

Usage:
    python3 validate_post.py POST.md [POST2.md ...]
    python3 validate_post.py --dir path/to/posts
    python3 validate_post.py --dir path/to/posts --json
"""
import argparse
import glob
import json
import os
import re
import sys

try:
    import yaml  # frontmatter must parse as real YAML, not merely look right
except ImportError:
    yaml = None

HERE = os.path.dirname(os.path.abspath(__file__))
# apps.json may sit beside this script (vendored into a repo) or in the skill's
# shared/ directory. Check both rather than assuming one layout.
_CANDIDATES = [
    os.path.join(HERE, "apps.json"),
    os.path.normpath(os.path.join(HERE, "..", "..", "shared", "apps.json")),
    os.path.normpath(os.path.join(HERE, "..", "shared", "apps.json")),
]
CATALOGUE = next((p for p in _CANDIDATES if os.path.exists(p)), _CANDIDATES[0])

# Post classes. `app` is the default and the strictest.
#   app          - sells one in-store app, cites the study behind it
#   science      - explainer or pre-launch; must cite, app CTA optional
#   announcement - company news / PR; no citation or app required
VALID_TYPES = ("app", "science", "announcement")

REQUIRED_FM = {
    "app": ["title", "description", "tags", "date", "app_id", "layout", "permalink"],
    "science": ["title", "description", "tags", "date", "layout", "permalink"],
    "announcement": ["title", "tags", "date", "layout", "permalink"],
}

COMPETITORS = [
    "23andme", "ancestry.com", "myheritage", "familytreedna",
    "livingdna", "nebula.org", "promethease",
]

# Humour markers that must never appear in a health/medical post.
HEALTH_JOKE_MARKERS = [
    "lol", "haha", "just kidding", "no dragons required", "party trick",
    "wingardium", "hogwarts", "jedi", "cosmic alignment", "star sign",
    "potluck", "brag", "bragging rights", "guess my", "spoiler alert",
    "surprise party", "skittles", "monocle",
]

# EN / FR / NL - the corpus is trilingual
HEALTH_TERMS = [
    # en
    "cancer", "tumour", "tumor", "brca", "disease", "disorder", "syndrome",
    "diagnosis", "diagnose", "risk of", "treatment", "therapy", "patient",
    "depression", "alzheimer", "diabetes", "carrier", "mutation", "pathogenic",
    "symptom", "clinical", "prognosis", "medication", "drug",
    # fr
    "maladie", "trouble", "diagnostic", "diagnostiqu", "traitement", "th\u00e9rapie",
    "d\u00e9pression", "depressif", "d\u00e9pressif", "risque de", "sympt\u00f4me", "clinique",
    "m\u00e9dicament", "cancer", "pronostic", "porteur",
    # nl
    "ziekte", "aandoening", "diagnose", "behandeling", "depressie", "risico op",
    "symptoom", "klinisch", "geneesmiddel", "drager",
]

CITATION_RE = re.compile(
    r"(doi\.org/10\.\d{4,}|10\.\d{4,}/[^\s)\]]+|pubmed\.ncbi\.nlm\.nih\.gov/\d+"
    r"|ncbi\.nlm\.nih\.gov/pubmed/\d+|PMID[:\s]*\d+|pmc\.ncbi\.nlm\.nih\.gov/articles/PMC\d+)",
    re.I,
)
RSID_RE = re.compile(r"\brs\d{3,}\b")
APP_LINK_RE = re.compile(r"geneplaza\.com/app-store/(\d+)", re.I)
# GenePlaza's platform framing: an app score says where you would have scored had
# you taken part in the original study, in that cohort. It is NOT a statement that
# the reader personally has raised or lowered risk. Posts must not invert this.
READER_RISK_RE = re.compile(
    r"\byour (own )?(risk|chance|odds|probability) of\b"
    r"|\b(increases|raises|lowers|reduces) your (risk|chance|odds)\b"
    r"|\byou (have|carry|are at) (an? )?(increased|elevated|higher|lower|reduced|decreased) risk\b"
    r"|\bputs you at (increased |higher )?risk\b"
    r"|\bvotre risque de\b|\baugmente votre risque\b"
    r"|\buw risico op\b|\bverhoogt uw risico\b",
    re.I,
)
# Evidence the post uses cohort-position framing rather than personal-risk framing.
COHORT_FRAMING_RE = re.compile(
    r"would have (been|scored)|had you (taken part|participated)|if you had participated"
    r"|where (you|your \w+) (would )?(fall|fell|sit|sits|would have)"
    r"|would (have been placed|sit|fall)"
    r"|had it been included|on the distribution|within (that|this) cohort"
    r"|position on (the|that) distribution"
    r"|si vous aviez participé|vous situe sur la distribution|où vous vous situez"
    r"|als u had deelgenomen|waar u op de verdeling",
    re.I,
)

# A *specific* scientific assertion, as opposed to health-adjacent vocabulary or
# a product name. Used to decide whether an announcement is obliged to cite.
SCIENTIFIC_CLAIM_RE = re.compile(
    r"\brs\d{3,}\b"                                    # a variant
    r"|\b\d+(\.\d+)?\s?%"                               # a percentage
    r"|\b\d+(\.\d+)?\s?(times|x)\s+(more|less|higher|lower)"
    r"|\bodds ratio\b|\bp\s?[<=]\s?0?\.\d"
    r"|\b(study|research|trial|meta-analysis)\s+(show|found|report|reveal|suggest|conclud)"
    r"|\b(l'|une |des )?\u00e9tudes?\s+(montre|r\u00e9v\u00e8le|sugg\u00e8re|conclut|a montr\u00e9)"
    r"|\b(onderzoek|studie)\s+(toont|blijkt|wijst|concludeert)",
    re.I,
)
# generic store link = /app-store not immediately followed by /<digits>
GENERIC_STORE_RE = re.compile(r"geneplaza\.com/app-store(?!/\d)", re.I)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def load_catalogue():
    if not os.path.exists(CATALOGUE):
        return None
    with open(CATALOGUE) as f:
        return {a["id"]: a for a in json.load(f)}


def split_frontmatter(text):
    """Return (frontmatter_dict, body, errors). Strict about position."""
    errors = []
    if not text.startswith("---"):
        errors.append(
            "FRONTMATTER: file does not start with '---' at column 0 "
            "(leading blank line or indentation breaks 11ty YAML parsing)"
        )
        stripped = text.lstrip()
        if stripped.lstrip().startswith("---"):
            m = re.search(r"^\s*---(.*?)^\s*---", text, re.S | re.M)
            if m:
                return parse_fm_block(m.group(1)), text[m.end():], errors
        return {}, text, errors

    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        errors.append("FRONTMATTER: opening '---' has no matching closing '---'")
        return {}, text, errors

    # A regex parse happily reads frontmatter that YAML rejects - e.g. an unquoted
    # value containing ': '. 11ty uses a real YAML parser and fails the build, so
    # check with one here rather than discovering it at build time.
    if yaml is not None:
        try:
            yaml.safe_load(m.group(1))
        except Exception as e:
            errors.append(
                "FRONTMATTER: not valid YAML - 11ty will fail to build this file "
                f"({str(e).splitlines()[0]}). Quote any value containing ': '"
            )

    return parse_fm_block(m.group(1)), text[m.end():], errors


def parse_fm_block(block):
    fm = {}
    for line in block.splitlines():
        if re.match(r"^\s*#", line) or not line.strip():
            continue
        m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def validate(path, catalogue):
    text = open(path, encoding="utf-8", errors="replace").read()
    fm, body, errors = split_frontmatter(text)
    warnings = []
    low_body = body.lower()

    ptype = str(fm.get("type", "app")).strip().strip("\"'").lower() or "app"
    if ptype == "unclassified":
        hint = str(fm.get("type_suggestion", "")).strip().strip("\"'")
        errors.append(
            "FRONTMATTER: type is 'unclassified' - decide app/science/announcement "
            f"before publishing{f' (exporter suggested: {hint}, unverified)' if hint else ''}"
        )
        ptype = "science"  # validate against the middle tier meanwhile
    elif ptype not in VALID_TYPES:
        errors.append(f"FRONTMATTER: type '{ptype}' invalid - use one of {VALID_TYPES}")
        ptype = "app"

    # --- frontmatter completeness
    for key in REQUIRED_FM[ptype]:
        if key not in fm or not fm[key]:
            errors.append(f"FRONTMATTER: missing required field '{key}'")
    if ptype == "announcement" and not fm.get("description"):
        warnings.append("FRONTMATTER: no description - weakens the search snippet")

    # --- CTA resolves to a real in-store app
    app_ids = set(APP_LINK_RE.findall(text))
    if not app_ids:
        msg = "CTA: no link to a specific app (need geneplaza.com/app-store/<id>)"
        (errors if ptype == "app" else warnings).append(msg)
    if GENERIC_STORE_RE.search(text):
        msg = "CTA: generic /app-store link - must deep-link to the app being sold"
        (errors if ptype == "app" else warnings).append(msg)

    if catalogue is not None:
        for aid in app_ids:
            if aid not in catalogue:
                errors.append(f"CTA: app id {aid} is not an in-store GenePlaza app")
        fm_app = str(fm.get("app_id", "")).strip().strip("\"'")
        if fm_app:
            if catalogue and fm_app not in catalogue:
                errors.append(f"FRONTMATTER: app_id {fm_app} is not an in-store GenePlaza app")
            elif fm_app not in app_ids:
                errors.append(
                    f"CTA: frontmatter app_id {fm_app} is never linked in the body"
                )

    # --- competitor promotion
    # A stated `competitor_context:` justifies mentions - e.g. inbound-migration
    # posts telling FamilyTreeDNA/MyHeritage users how to upload data to GenePlaza.
    # The placeholder written by the WP exporter does NOT count as justification.
    ctx = str(fm.get("competitor_context", "")).strip().strip("\"'")
    justified = bool(ctx) and not ctx.upper().startswith("REVIEW")
    if ctx and not justified:
        errors.append(
            "COMPETITOR: competitor_context is still the unreviewed placeholder - "
            "a human must confirm the context and state the reason"
        )

    for comp in COMPETITORS:
        if comp in text.lower():
            hits = len(re.findall(re.escape(comp), text, re.I))
            linked = re.search(r"https?://[^\s)>]*" + re.escape(comp), text, re.I)
            if justified:
                warnings.append(
                    f"COMPETITOR: '{comp}' ({hits}x{', linked' if linked else ''}) "
                    f"allowed by competitor_context: {ctx[:60]}"
                )
            elif linked:
                errors.append(
                    f"COMPETITOR: outbound link to '{comp}' ({hits} mention(s)) - "
                    "never pass link equity to a competitor "
                    "(set competitor_context if this is justified)"
                )
            else:
                warnings.append(f"COMPETITOR: '{comp}' mentioned {hits}x with no link - justify or remove")

    # --- hotlinked images
    for src in MD_IMAGE_RE.findall(body):
        if src.startswith("http"):
            errors.append(f"IMAGE: hotlinked external image '{src[:70]}' - host it yourself")

    # --- citations
    citations = CITATION_RE.findall(text)
    if not citations:
        msg = "CITATION: no DOI/PMID/PubMed reference anywhere in the post"
        if ptype == "announcement":
            # Health-adjacent vocabulary and product names ("Depression App") are
            # not claims. Only a concrete assertion obliges an announcement to cite.
            claim = SCIENTIFIC_CLAIM_RE.search(body)
            if claim:
                errors.append(
                    msg + f" - announcement makes a specific scientific claim "
                    f"({claim.group(0)[:40]!r}), so it must cite"
                )
        else:
            errors.append(msg)
    elif len(set(citations)) < 2 and ptype != "announcement":
        warnings.append(
            f"CITATION: only {len(set(citations))} unique source - "
            "aim for the app's own study plus at least one corroborating source"
        )

    # --- the app's own study must be cited
    # Prefer the curated frontmatter `study:` field. The catalogue's `developer`
    # string is unreliable free text (e.g. "Based on the study of Naomi R., et al."
    # yields a first name, not a surname), so it is only ever a warning.
    if ptype == "app":
        SKIP = {"From", "Based", "Study", "University", "Institute", "Medicine",
                "Center", "Centre", "College", "School", "Department", "Genomics",
                "Australia", "Netherlands", "Broad", "Queensland", "Northwestern",
                "Nature", "Genetics", "Science", "Psychiatry", "Neuroscience",
                "Molecular", "Journal", "Consultants", "Genomic", "Algorithms"}

        def name_tokens(s):
            return [t for t in re.findall(r"\b([A-Z][a-z]{2,})\b", s or "") if t not in SKIP]

        fm_study = str(fm.get("study", "")).strip().strip("\"'")
        if fm_study:
            cands = name_tokens(fm_study)
            if cands and not any(re.search(rf"\b{re.escape(c)}\b", body, re.I) for c in cands):
                errors.append(
                    f"CITATION: frontmatter study {cands[:3]} is never referenced in the body"
                )
        elif catalogue:
            app = catalogue.get(str(fm.get("app_id", "")).strip().strip("\"'"))
            if app and app.get("study"):
                cands = name_tokens(app["study"])
                if cands and not any(re.search(rf"\b{re.escape(c)}\b", text, re.I) for c in cands):
                    warnings.append(
                        f"CITATION: no frontmatter `study:` and the catalogue's study "
                        f"{cands[:3]} is not referenced - add `study:` naming the paper"
                    )

    # --- concrete genetics
    if not RSID_RE.search(body) and ptype != "announcement":
        warnings.append("SPECIFICITY: no rsID named - post may be too vague to rank or to be verifiable")

    # --- health tone
    health_hits = [t for t in HEALTH_TERMS if t in low_body]
    # One passing mention (e.g. "disease" in an archaeology post) is not health
    # content. Require either several distinct terms or repeated use of one.
    if health_hits and (len(health_hits) > 2 or
                        any(low_body.count(t) >= 3 for t in health_hits)):
        jokes = [j for j in HEALTH_JOKE_MARKERS if j in low_body]
        if jokes:
            errors.append(
                f"TONE: health content (matched {health_hits[:3]}) contains humour markers "
                f"{jokes[:4]} - no jokes on health claims"
            )
        disclaimer = (
            # en
            r"not (a |an )?(medical|diagnostic|diagnosis|substitute)"
            r"|does not diagnose|not intended to diagnose|cannot tell you whether"
            r"|predisposition,? not (a )?diagnosis"
            r"|(consult|speak|talk|conversation|discuss)\b[^.]{0,60}"
            r"(doctor|physician|clinician|healthcare|genetic counsel)"
            # fr
            r"|pas d[eu']{1,3} ?diagnostic|ne diagnostique pas|non (pas )?un diagnostic"
            r"|pr\u00e9disposition[^.]{0,40}pas d[eu']{1,3} ?diagnostic"
            r"|(consultez|parlez|conversation|adressez|revient)\b[^.]{0,60}"
            r"(m\u00e9decin|clinicien|professionnel de sant\u00e9|conseil g\u00e9n\u00e9tique)"
            # nl
            r"|geen diagnose|niet diagnostisch|stelt geen diagnose"
            r"|(raadpleeg|bespreek|overleg)\b[^.]{0,60}"
            r"(arts|dokter|zorgverlener|genetisch consulent)"
            # standalone signposting to clinical genetics in any language
            r"|genetic counsel|clinical genetic testing"
            r"|conseil g\u00e9n\u00e9tique|test g\u00e9n\u00e9tique clinique"
            r"|genetisch advies|klinisch genetisch"
        )
        if not re.search(disclaimer, low_body):
            warnings.append("TONE: health content with no medical disclaimer / signposting to a clinician")

    # --- house voice: the opening must land on something concrete
    # (a scene, a person, a year, a number, or direct address) rather than an
    # institution or an abstract noun. See write-post/VOICES.md.
    paras = [p.strip() for p in re.split(r"\n\s*\n", body)
             if p.strip() and not p.strip().startswith(("#", "|", ">", "!", "*", "-"))]
    if paras and ptype != "announcement":
        opening = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", paras[0])
        opening = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", opening)
        concrete = re.search(
            r"\d[\d\s,\.]{2,}"                                   # any number of size
            r"|\b(1[6-9]\d{2}|20[0-2]\d)\b"                       # a year
            r"|\byou\b|\byour\b|\bvous\b|\bvotre\b|\buw\b"        # direct address
            r"|\b(someone|somebody|some people|a person|a man|a woman|a child"
            r"|children|brothers|sisters|workmen|patients?|participants?)\b"
            r"|\b(quelqu'un|une personne|un enfant|enfants|ouvriers)\b"
            r"|\b(iemand|kinderen|mensen)\b"
            r"|\b(five|six|seven|eight|nine|ten)-year-old\b"
            r"|\bBC\b|\bAD\b|av\. J\.-C\.|avant notre \u00e8re"
            r"|\b(getting|imagine|picture|open(ing)? your)\b",
            opening, re.I,
        )
        if not concrete:
            warnings.append(
                "VOICE: opening paragraph has no concrete anchor (scene, person, year, "
                "number or direct address) - house style opens on something specific, "
                "not on an institution or abstract noun"
            )

    # --- score framing: cohort position, never personal risk
    # Explicitly denying the framing ("it is NOT a statement that your risk is
    # raised") is the correct thing to write, so skip negated occurrences.
    for m in READER_RISK_RE.finditer(body):
        ctx = body[max(0, m.start() - 80):m.start()].lower()
        if re.search(r"\b(not|never|no|isn't|is not|does not|cannot|rather than|instead of"
                     r"|ne |pas |niet |geen)\b[^.]{0,60}$", ctx):
            continue
        errors.append(
            f"FRAMING: {m.group(0)!r} attributes risk to the reader. A GenePlaza score "
            "says where they would have scored had they taken part in the original "
            "study, in that cohort - not that they personally have raised risk"
        )
        break
    if ptype == "app" and not COHORT_FRAMING_RE.search(body):
        warnings.append(
            "FRAMING: no cohort-position wording found - state that the score shows "
            "where the reader would have fallen in the original study population"
        )

    # --- absolute-risk language
    # Negated forms ("does not guarantee", "ne garantit pas") are hedges, not claims.
    NEG = r"(?<!not )(?<!n't )(?<!never )(?<!no )"
    determinist = (
        r"\byou will (get|develop)\b"
        r"|" + NEG + r"\bguarantees?\b"
        r"|\bwill definitely\b"
        r"|\bvous (allez|aurez) (d\u00e9velopper|certainement)\b"
        r"|" + NEG + r"\bgarantit\b"
    )
    for m in re.finditer(determinist, low_body):
        ctx = low_body[max(0, m.start() - 40):m.start()]
        if re.search(r"\b(not|never|no|ne|pas|n'est|does not|cannot)\b[^.]{0,30}$", ctx):
            continue  # negated - this is a hedge
        errors.append(
            f"CLAIM: deterministic risk language {m.group(0)!r} - "
            "genetic predisposition is probabilistic"
        )
        break

    return {
        "path": path,
        "type": ptype,
        "errors": errors,
        "warnings": warnings,
        "citations": sorted(set(citations)),
        "app_ids": sorted(app_ids),
        "passed": not errors,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="*")
    ap.add_argument("--dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths = list(args.posts)
    if args.dir:
        paths += sorted(glob.glob(os.path.join(args.dir, "*.md")))
    if not paths:
        sys.exit("No posts given. Use POST.md or --dir DIR")

    catalogue = load_catalogue()
    if catalogue is None:
        print("WARNING: no apps.json cache; run shared/app_catalogue.py --refresh\n", file=sys.stderr)

    results = [validate(p, catalogue) for p in paths]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"\n{status}  {os.path.basename(r['path'])}  [{r['type']}]")
            for e in r["errors"]:
                print(f"   [ERROR] {e}")
            for w in r["warnings"]:
                print(f"   [warn ] {w}")
        n_pass = sum(1 for r in results if r["passed"])
        print(f"\n{'='*60}\n{n_pass}/{len(results)} passed")

    sys.exit(0 if all(r["passed"] for r in results) else 1)


if __name__ == "__main__":
    main()
