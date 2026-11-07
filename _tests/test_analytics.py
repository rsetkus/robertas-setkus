"""counter.dev analytics script in production pages (feature: analytics).

Tests assert on the built site only. See _docs/testing.md.
"""

import re
from pathlib import Path

import pytest
import yaml
from bs4 import Tag

from conftest import FIXTURE_POSTS, REPO_ROOT, build, build_log, html, xml

SCRIPT_SRC = "https://cdn.counter.dev/script.js"
SITE_ID = "cee64376-9fee-402d-98b4-58246fa7413a"
UTCOFFSET = "2"

# Every page in STORY-1 AC1. The post comes from _tests/fixtures/posts/.
PAGES = [
    "index.html",
    "blog/index.html",
    "resume/index.html",
    "torch-privacy-policy/index.html",
    "blog/2026/fixture-post/index.html",
]

TEST_ID = "00000000-0000-0000-0000-000000000000"


def _counter_scripts(page):
    return page.find_all("script", src=SCRIPT_SRC)


def _the_counter_script(site, path):
    scripts = _counter_scripts(html(site, path))
    assert len(scripts) == 1, (
        f"{path}: expected one counter.dev script, found {len(scripts)}")
    return scripts[0]


# --- STORY-1 ---------------------------------------------------------------

@pytest.mark.parametrize("path", PAGES)
def test_story_1_counter_script_is_in_head_once(fixture_site, path):
    """AC1: exactly one counter.dev script on the page, inside <head>."""
    script = _the_counter_script(fixture_site, path)
    assert script.find_parent("head") is not None, (
        f"{path}: the counter.dev script is not inside <head>")


@pytest.mark.parametrize("path", PAGES)
def test_story_1_counter_script_has_site_id_and_utcoffset(fixture_site, path):
    """AC2: the script carries the site id and UTC offset from _config.yml."""
    script = _the_counter_script(fixture_site, path)
    assert script.get("data-id") == SITE_ID
    assert script.get("data-utcoffset") == UTCOFFSET


@pytest.mark.parametrize("path", PAGES)
def test_story_1_counter_script_is_the_plain_snippet(fixture_site, path):
    """AC3: only src, data-id and data-utcoffset; no async/defer/type; no text."""
    script = _the_counter_script(fixture_site, path)
    assert set(script.attrs) == {"src", "data-id", "data-utcoffset"}, (
        f"{path}: unexpected attributes {sorted(script.attrs)}")
    for attr in ("async", "defer", "type"):
        assert not script.has_attr(attr), f"{path}: script has {attr}"
    assert script.get_text() == "", f"{path}: script has text content"


@pytest.mark.parametrize("path", PAGES)
def test_story_1_counter_script_is_last_in_head(fixture_site, path):
    """AC4: the script is the last element child of <head>."""
    page = html(fixture_site, path)
    scripts = _counter_scripts(page)
    assert len(scripts) == 1, (
        f"{path}: expected one counter.dev script, found {len(scripts)}")
    head = page.find("head")
    assert head is not None, f"{path} has no <head>"
    elements = [child for child in head.children if isinstance(child, Tag)]
    assert elements and elements[-1] is scripts[0], (
        f"{path}: the last element in <head> is "
        f"<{elements[-1].name if elements else 'nothing'}>, not the counter.dev script")


def test_story_1_every_html_file_has_counter_once(fixture_site):
    """AC5: every built .html file mentions cdn.counter.dev exactly once."""
    files = sorted(Path(fixture_site).rglob("*.html"))
    assert files, "no .html files were built"
    counts = {
        f.relative_to(fixture_site).as_posix():
            f.read_text(encoding="utf-8").count("cdn.counter.dev")
        for f in files
    }
    wrong = {path: n for path, n in counts.items() if n != 1}
    assert wrong == {}, f"files without exactly one cdn.counter.dev: {wrong}"
    assert "blog/2026/fixture-post/index.html" in counts


def test_story_1_feed_has_no_script(fixture_site):
    """AC6: feed.xml has no <script> and never mentions cdn.counter.dev."""
    feed = xml(fixture_site, "feed.xml")
    assert feed.find_all("script") == []
    text = (Path(fixture_site) / "feed.xml").read_text(encoding="utf-8")
    assert "cdn.counter.dev" not in text


@pytest.fixture(scope="module")
def custom_id_site(tmp_path_factory):
    """A production build whose config sets a different id and utcoffset."""
    return build(
        tmp_path_factory.mktemp("analytics-custom-id"),
        config={"analytics": {"counter_dev": {"id": TEST_ID, "utcoffset": 3}}},
    )


@pytest.mark.parametrize("path", [
    "index.html",
    "blog/index.html",
    "torch-privacy-policy/index.html",
])
def test_story_1_counter_values_come_from_config(custom_id_site, path):
    """AC7: data-id and data-utcoffset follow analytics.counter_dev in the config."""
    script = _the_counter_script(custom_id_site, path)
    assert script.get("data-id") == TEST_ID
    assert script.get("data-utcoffset") == "3"


# --- STORY-2 ---------------------------------------------------------------

def _html_files(site):
    files = sorted(Path(site).rglob("*.html"))
    assert files, "no .html files were built"
    return files


def _files_with_counter(site):
    """Built .html files (relative paths) that mention cdn.counter.dev."""
    return [
        f.relative_to(site).as_posix()
        for f in _html_files(site)
        if "cdn.counter.dev" in f.read_text(encoding="utf-8")
    ]


def test_story_2_dev_preview_has_no_counter(dev_site):
    """AC8: JEKYLL_ENV=development with _config.dev.yml: no page has the script,
    the pages of the drafts in _drafts/ included."""
    built = [f.relative_to(dev_site).as_posix() for f in _html_files(dev_site)]
    draft_slugs = sorted(p.stem for p in (REPO_ROOT / "_drafts").glob("*.md"))
    assert draft_slugs, "_drafts/ has no drafts to check"
    for slug in draft_slugs:
        assert any(slug in path for path in built), (
            f"the draft {slug} was not built in the dev preview")
    assert _files_with_counter(dev_site) == []


def test_story_2_plain_development_build_has_no_counter(tmp_path):
    """AC9: _config.yml only with JEKYLL_ENV=development (plain jekyll serve)."""
    site = build(tmp_path, env="development")
    assert (Path(site) / "index.html").is_file()
    assert _files_with_counter(site) == []


def test_story_2_no_analytics_section_builds_without_counter(tmp_path):
    """AC10: production build with no analytics section succeeds, no script."""
    site = build(tmp_path, remove=["analytics"])
    for path in ("index.html", "blog/index.html", "resume/index.html",
                 "torch-privacy-policy/index.html"):
        assert (Path(site) / path).is_file(), f"{path} was not built"
    assert _files_with_counter(site) == []


@pytest.mark.parametrize("settings", [
    {"remove": ["analytics.counter_dev.id"]},
    {"config": {"analytics": {"counter_dev": {"id": ""}}}},
], ids=["no-id-key", "empty-id"])
def test_story_2_missing_or_empty_id_has_no_counter(tmp_path, settings):
    """AC11: production build with no id key, or with id: "", has no script."""
    site = build(tmp_path, **settings)
    assert (Path(site) / "index.html").is_file()
    assert _files_with_counter(site) == []


def test_story_2_dev_config_has_no_analytics_key():
    """AC12: _config.dev.yml, loaded as YAML, has no analytics key."""
    data = yaml.safe_load(
        (REPO_ROOT / "_config.dev.yml").read_text(encoding="utf-8")) or {}
    assert isinstance(data, dict)
    assert "analytics" not in data


# --- STORY-3 ---------------------------------------------------------------

@pytest.fixture(scope="module")
def no_id_site(tmp_path_factory):
    """A production build with the fixture posts and no analytics.counter_dev.id."""
    return build(tmp_path_factory.mktemp("analytics-no-id"),
                 posts=sorted(FIXTURE_POSTS.glob("*.md")),
                 remove=["analytics.counter_dev.id"])


def _without_counter(site, path):
    """The page's <head> and <body> children, with every cdn.counter.dev
    <script> removed and whitespace between tags ignored."""
    page = html(site, path)
    for script in page.find_all("script", src=True):
        if "cdn.counter.dev" in script["src"]:
            script.decompose()

    def children(parent_name):
        parent = page.find(parent_name)
        assert parent is not None, f"{path} has no <{parent_name}>"
        return [re.sub(r">\s+<", "><", str(child)).strip()
                for child in parent.children
                if isinstance(child, Tag) or str(child).strip()]

    return children("head"), children("body")


@pytest.mark.parametrize("path", PAGES)
def test_story_3_page_matches_build_without_analytics(fixture_site, no_id_site, path):
    """AC13: apart from the counter.dev script, <head> and <body> are the same
    as in a production build whose config has no analytics.counter_dev.id."""
    shipped_head, shipped_body = _without_counter(fixture_site, path)
    plain_head, plain_body = _without_counter(no_id_site, path)
    assert shipped_head == plain_head, f"{path}: <head> differs"
    assert shipped_body == plain_body, f"{path}: <body> differs"


def test_story_3_production_build_prints_no_warnings(fixture_site):
    """AC14: the production build with the fixture posts exits 0 (fixture_site
    raises BuildError otherwise) and prints no Warning or Deprecation line."""
    assert (Path(fixture_site) / "blog/2026/fixture-post/index.html").is_file()
    noisy = [line for line in build_log(fixture_site).splitlines()
             if "Warning" in line or "Deprecation" in line]
    assert noisy == [], "the production build printed:\n" + "\n".join(noisy)


@pytest.mark.skip(reason="visual: AC15 -- /, /blog/, /resume/, /torch-privacy-policy/ "
                         "and a post look the same as before the change at desktop "
                         "width and at 375 px (no shift, gap or extra element)")
def test_story_3_pages_look_unchanged_on_desktop_and_phone():
    ...


@pytest.mark.skip(reason="visual (after deploy): AC16 -- opening https://setkus.lt/ "
                         "shows a request to cdn.counter.dev/script.js in the network "
                         "tab, and the visit appears in the counter.dev dashboard "
                         "within a few minutes")
def test_story_3_live_site_loads_counter_and_counts_visit():
    ...
