"""Regression tests that belong to no Sage story.

Named test_baseline_* so story selectors (-k "story_<N>_") never pick them up.
The full suite, which the EpicVerifier runs, always includes them.
"""

from pathlib import Path

import pytest

from conftest import exists, html, xml

DEMO_SLUGS = ["everything-a-post-can-do", "sharing-ktor-client-kmp"]


def _built_paths(site):
    return [p.relative_to(site).as_posix() for p in Path(site).rglob("*")]


def test_baseline_production_has_no_demo_content(prod_site):
    assert not exists(prod_site, "assets/demo")
    for slug in DEMO_SLUGS:
        leaks = [p for p in _built_paths(prod_site) if slug in p]
        assert leaks == [], f"demo post {slug} is in the production build: {leaks}"


@pytest.mark.parametrize("name", [
    "AGENTS.md", "AGENTS.html", "CLAUDE.md", "CLAUDE.html", "sage-config.yaml",
    "_tests", "_docs", "_prds", "_output", "_templates", "_drafts",
])
def test_baseline_production_has_no_repo_only_files(prod_site, name):
    assert not exists(prod_site, name)


@pytest.mark.parametrize("path", [
    "index.html",
    "blog/index.html",
    "resume/index.html",
    "feed.xml",
    "torch-privacy-policy/index.html",
])
def test_baseline_main_pages_exist(prod_site, path):
    assert exists(prod_site, path)


def test_baseline_fixture_post_is_built_listed_and_in_feed(fixture_site):
    url = "/blog/2026/fixture-post/"
    page = html(fixture_site, "blog/2026/fixture-post/index.html")
    assert page.find("h1").get_text(strip=True) == "Fixture post for tests"

    index = html(fixture_site, "blog/index.html")
    assert url in [a.get("href") for a in index.select("ol.posts a")]

    feed = xml(fixture_site, "feed.xml")
    titles = [t.get_text(strip=True) for t in feed.select("entry > title")]
    assert "Fixture post for tests" in titles


def test_baseline_dev_build_shows_demo_post(dev_site):
    built = _built_paths(dev_site)
    assert any(p.endswith("everything-a-post-can-do/index.html") for p in built)
    assert exists(dev_site, "assets/demo")
