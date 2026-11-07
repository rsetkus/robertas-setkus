"""Tests for the "Analytics" note in AGENTS.md (feature: analytics, STORY-4).

_docs/testing.md says tests check the built site. AGENTS.md is a repo-only file
that Jekyll excludes from the build, so the AC17 tests have to read it straight
from the repository: there is no built page to check. The spec names this as an
allowed exception. AC18 checks the production build as usual.
"""

import re
from pathlib import Path

from conftest import REPO_ROOT, exists

AGENTS_MD = REPO_ROOT / "AGENTS.md"
SECTION_HEADING = "## How the site fits together"


def _section():
    """Text between the "How the site fits together" heading and the next ## heading."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == SECTION_HEADING]
    assert starts, f'AGENTS.md has no "{SECTION_HEADING}" heading'
    body = []
    for line in lines[starts[0] + 1:]:
        if re.match(r"^##\s", line):
            break
        body.append(line)
    return body


def _analytics_bullet():
    """The top-level bullet in the section that starts with **Analytics, with its
    wrapped and nested lines, joined into one string."""
    body = _section()
    starts = [i for i, line in enumerate(body) if re.match(r"^- \*\*Analytics\b", line)]
    assert starts, (
        f'"{SECTION_HEADING}" in AGENTS.md has no bullet starting with **Analytics**'
    )
    bullet = [body[starts[0]]]
    for line in body[starts[0] + 1:]:
        if re.match(r"^- ", line):
            break
        bullet.append(line)
    return " ".join(line.strip() for line in bullet)


def test_story_4_agents_md_has_analytics_bullet():
    """AC17: the section has a bullet that starts with **Analytics**."""
    assert _analytics_bullet().startswith("- **Analytics")


def test_story_4_agents_md_analytics_names_config_settings():
    """AC17: the bullet says the settings live in _config.yml under analytics.counter_dev."""
    bullet = _analytics_bullet()
    assert "_config.yml" in bullet, f"Analytics bullet does not mention _config.yml: {bullet}"
    assert "analytics.counter_dev" in bullet, (
        f"Analytics bullet does not mention analytics.counter_dev: {bullet}"
    )


def test_story_4_agents_md_analytics_says_production_only():
    """AC17: the bullet says the script loads only in production."""
    bullet = _analytics_bullet().lower()
    assert "production" in bullet, f"Analytics bullet does not mention production: {bullet}"
    assert re.search(r"\bonly\b", bullet), (
        f'Analytics bullet does not say the script loads "only" in production: {bullet}'
    )


def test_story_4_agents_md_analytics_says_new_layout_must_include_it():
    """AC17: the bullet says a new layout must include analytics.html in its <head>."""
    bullet = _analytics_bullet()
    assert "analytics.html" in bullet, f"Analytics bullet does not mention analytics.html: {bullet}"
    assert "<head>" in bullet, f"Analytics bullet does not mention <head>: {bullet}"
    assert re.search(r"\blayouts?\b", bullet, re.IGNORECASE), (
        f"Analytics bullet does not say a new layout must include it: {bullet}"
    )


def test_story_4_production_build_has_no_agents_file(prod_site):
    """AC18: the production build contains no AGENTS.md or AGENTS.html, anywhere."""
    assert not exists(prod_site, "AGENTS.md")
    assert not exists(prod_site, "AGENTS.html")
    leaks = [
        p.relative_to(prod_site).as_posix()
        for p in Path(prod_site).rglob("*")
        if p.name in ("AGENTS.md", "AGENTS.html")
    ]
    assert leaks == [], f"AGENTS file is in the production build: {leaks}"
