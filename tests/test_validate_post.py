"""
Regression tests for the post validator.

Every test here corresponds to a bug that actually shipped and was caught later —
usually by building the site rather than by checking markdown. They exist so the
same class of mistake fails in CI instead of in production.
"""
import os
import subprocess
import sys
import textwrap

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import validate_post as V  # noqa: E402

CATALOGUE = V.load_catalogue()


def make(tmp_path, body, **fm):
    """Write a post with sensible defaults, overridden by kwargs."""
    front = {
        "title": '"Test post"',
        "type": "app",
        "description": "A description with enough words to be plausible.",
        "tags": '["post"]',
        "date": "2024-01-01",
        "lang": "en",
        "app_id": "61",
        "study": '"Cornelis MC et al., Molecular Psychiatry 2015"',
        "layout": "article.njk",
        "permalink": '"blog/en/test/index.html"',
    }
    front.update({k: v for k, v in fm.items() if v is not None})
    for k, v in list(front.items()):
        if v is V.__class__:  # unreachable; keeps linters quiet
            pass
    drop = [k for k, v in fm.items() if v is None]
    for k in drop:
        front.pop(k, None)
    block = "\n".join(f"{k}: {v}" for k, v in front.items())
    p = tmp_path / "post.md"
    p.write_text(f"---\n{block}\n---\n\n{textwrap.dedent(body)}\n", encoding="utf-8")
    return str(p)


GOOD_BODY = """
    In 1903, workmen digging a trench found something unexpected.

    Cornelis and colleagues showed the effect in a large cohort
    ([paper](https://doi.org/10.1038/mp.2014.107), PMID: 25288136) and it was
    corroborated elsewhere ([second](https://doi.org/10.1001/jama.295.10.1135)).
    The variant rs762551 is the one usually cited.

    The [Coffee Metabolism app](https://www.geneplaza.com/app-store/61) shows where
    you would have fallen among the participants had you taken part in that study.
    It is not a diagnosis; speak to your doctor about medication.
"""


def errors_for(path):
    r = V.validate(path, CATALOGUE)
    return r["errors"]


def test_good_post_passes(tmp_path):
    assert errors_for(make(tmp_path, GOOD_BODY)) == []


# --- frontmatter -----------------------------------------------------------

def test_invalid_yaml_is_an_error(tmp_path):
    """Broke the entire 11ty build in production. Regex parsing missed it."""
    p = make(tmp_path, GOOD_BODY, description="Broken: yes, really")
    assert any("not valid YAML" in e for e in errors_for(p))


def test_indented_frontmatter_is_an_error(tmp_path):
    p = tmp_path / "bad.md"
    p.write_text("\n            ---\n            title: x\n            ---\nbody\n", encoding="utf-8")
    assert any("column 0" in e for e in errors_for(str(p)))


def test_unclassified_type_blocks(tmp_path):
    p = make(tmp_path, GOOD_BODY, type="unclassified")
    assert any("unclassified" in e for e in errors_for(p))


# --- CTA -------------------------------------------------------------------

def test_generic_app_store_link_is_an_error(tmp_path):
    body = GOOD_BODY.replace(
        "https://www.geneplaza.com/app-store/61", "https://www.geneplaza.com/app-store"
    )
    assert any("generic /app-store" in e for e in errors_for(make(tmp_path, body)))


def test_deep_link_is_not_flagged_as_generic(tmp_path):
    """Regex backtracking once made /app-store/61 match the generic pattern."""
    assert not any("generic /app-store" in e for e in errors_for(make(tmp_path, GOOD_BODY)))


def test_app_id_must_be_linked_in_body(tmp_path):
    p = make(tmp_path, GOOD_BODY, app_id="54")
    assert any("never linked" in e for e in errors_for(p))


# --- competitors -----------------------------------------------------------

def test_competitor_link_is_an_error(tmp_path):
    body = GOOD_BODY + "\nUpload from [23andMe](https://www.23andme.com/).\n"
    assert any("COMPETITOR" in e for e in errors_for(make(tmp_path, body)))


def test_competitor_allowed_with_stated_context(tmp_path):
    body = GOOD_BODY + "\nUpload from [23andMe](https://www.23andme.com/).\n"
    p = make(tmp_path, body, competitor_context='"Inbound migration guide. Reviewed."')
    assert not any("COMPETITOR" in e for e in errors_for(p))


def test_competitor_placeholder_still_blocks(tmp_path):
    body = GOOD_BODY + "\nUpload from [23andMe](https://www.23andme.com/).\n"
    p = make(tmp_path, body, competitor_context="REVIEW - mentions 23andme; confirm")
    assert any("placeholder" in e for e in errors_for(p))


# --- claim framing ---------------------------------------------------------

def test_personal_risk_framing_is_an_error(tmp_path):
    body = GOOD_BODY + "\nThe app tells you your risk of heart disease.\n"
    assert any("FRAMING" in e for e in errors_for(make(tmp_path, body)))


def test_negated_risk_framing_is_allowed(tmp_path):
    """'not a statement that your risk is raised' is the correct thing to write."""
    body = GOOD_BODY + "\nIt is not a statement that your own risk of anything is raised.\n"
    assert not any("FRAMING" in e for e in errors_for(make(tmp_path, body)))


def test_deterministic_language_is_an_error(tmp_path):
    body = GOOD_BODY + "\nThis variant guarantees the condition.\n"
    assert any("CLAIM" in e for e in errors_for(make(tmp_path, body)))


def test_negated_guarantee_is_allowed(tmp_path):
    """'does not guarantee' is a hedge, not a deterministic claim."""
    body = GOOD_BODY + "\nA normal result does not guarantee a normal genotype.\n"
    assert not any("CLAIM" in e for e in errors_for(make(tmp_path, body)))


# --- tone ------------------------------------------------------------------

def test_humour_in_health_content_is_an_error(tmp_path):
    body = GOOD_BODY + (
        "\nYour cancer diagnosis risk is a great party trick at a potluck, "
        "no dragons required. Ask about treatment and symptoms.\n"
    )
    assert any("TONE" in e for e in errors_for(make(tmp_path, body)))


def test_single_health_word_does_not_trigger_tone_rule(tmp_path):
    """'disease' once in an archaeology post is not health content."""
    body = GOOD_BODY + "\nViolence, disease or migration could explain the turnover.\n"
    assert not any("TONE" in e for e in errors_for(make(tmp_path, body)))


# --- citations -------------------------------------------------------------

def test_missing_citation_is_an_error(tmp_path):
    body = """
        In 1903 something happened.
        The [app](https://www.geneplaza.com/app-store/61) shows where you would have
        fallen had you taken part.
    """
    assert any("CITATION" in e for e in errors_for(make(tmp_path, body)))


def test_announcement_without_claims_needs_no_citation(tmp_path):
    """A startup announcement listing 'Depression App' is not a scientific claim."""
    body = """
        In 2018 GenePlaza joined an accelerator. Our apps include the Depression App
        and the Intelligence App.
    """
    p = make(tmp_path, body, type="announcement", app_id=None, study=None)
    assert not any("CITATION" in e for e in errors_for(p))


def test_announcement_with_a_statistic_must_cite(tmp_path):
    body = "In 2018 we launched. A study showed 15% of people benefit.\n"
    p = make(tmp_path, body, type="announcement", app_id=None, study=None)
    assert any("CITATION" in e for e in errors_for(p))


# --- house voice -----------------------------------------------------------

def test_abstract_opening_warns(tmp_path):
    body = """
        The consortium of institutional partners has considered the abstract
        question of methodology and its implications for the field.

        Cornelis et al. ([doi](https://doi.org/10.1038/mp.2014.107), PMID: 25288136)
        and ([second](https://doi.org/10.1001/jama.295.10.1135)) rs762551.
        The [app](https://www.geneplaza.com/app-store/61) shows where you would have
        fallen. Not a diagnosis; consult your doctor.
    """
    r = V.validate(make(tmp_path, body), CATALOGUE)
    assert any("VOICE" in w for w in r["warnings"])


def test_scene_opening_does_not_warn(tmp_path):
    r = V.validate(make(tmp_path, GOOD_BODY), CATALOGUE)
    assert not any("VOICE" in w for w in r["warnings"])


# --- hotlinking ------------------------------------------------------------

def test_hotlinked_image_is_an_error(tmp_path):
    body = GOOD_BODY + "\n![x](https://example.com/pic.png)\n"
    assert any("IMAGE" in e for e in errors_for(make(tmp_path, body)))
