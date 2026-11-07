# Testing conventions (setkus.lt)

Jekyll skips folders that start with `_`, so nothing in `_tests/` or `_docs/` is published.

## Framework

- pytest with BeautifulSoup. Install once: `python -m pip install --user --break-system-packages -r _tests/requirements.txt`.
- Tests live in `_tests/`, one file per area: `test_<area>.py`, for example `test_blog.py`, `test_post_layout.py`, `test_feed.py`, `test_resume.py`.
- Tests check the **built site**: HTML elements, attributes, text, links, meta tags, feed entries, and whether files exist. Never assert on Liquid or CSS source.

## Story-scoped test naming (Sage convention)

Every story test is named `test_story_<N>_<what>`:

```python
def test_story_3_blog_index_lists_tags(fixture_site):
    ...
```

The Tester selects one story with `-k "story_<N>_"`. Keep the trailing underscore: without it, `story_1` also matches `story_10`.

If a test covers behavior from several stories (rare), prefix it with the highest story number and name the others in the docstring.

Tests named `test_baseline_*` belong to no story. They guard the whole site (no demo content in production, main pages exist) and run only in the full suite.

## Commands

- **One story (Tester):** `python -m pytest _tests/ -k "story_<N>_" -v --tb=short`
- **Full suite (EpicVerifier):** `python -m pytest _tests/ -v --tb=short`
- **One test by name:** `python -m pytest _tests/ -k "<substring>" -v`

pytest exit codes: 0 all passed, 1 tests failed, 2 usage error or `jekyll` missing, 5 no tests collected. Exit code 5 for a story selector is a failure: the story has no `test_story_<N>_` tests.

A failed `jekyll build` inside a fixture raises `BuildError` with Jekyll's stderr. Treat it as a build error, not a test failure.

## Fixtures (`_tests/conftest.py`)

Every build copies the site into a temporary folder and builds there, so tests never touch `_site/`, `.jekyll-cache/` or the real `_posts/`.

| Fixture or helper | What it gives you |
|---|---|
| `prod_site` | The real site, built like GitHub Pages (`JEKYLL_ENV=production`, `_config.yml` only) |
| `fixture_site` | A production build plus every post in `_tests/fixtures/posts/` |
| `dev_site` | A local-preview build with `_config.dev.yml` (drafts and demo content shown) |
| `build(tmp_path, posts=[...], dev=False)` | A custom build, for a story that needs its own posts |
| `html(site, "blog/index.html")` | The built page as BeautifulSoup |
| `xml(site, "feed.xml")` | The built feed as BeautifulSoup |
| `exists(site, "assets/demo")` | Whether a file or folder was built |

Session fixtures are shared, so tests must not modify the built files. A test that needs a different site calls `build(tmp_path, ...)` itself.

## Fixture posts

- Story tests use fixture posts, never real posts in `_posts/`, which change over time.
- Put new fixture posts in `_tests/fixtures/posts/`, named like real posts (`YYYY-MM-DD-slug.md`). Adding one changes `fixture_site` for every test, so check that existing tests still hold. Posts that only one test needs can go in a subfolder and be passed to `build(posts=...)`.
- Fixture posts are original test content. Never give one `demo: true`, and never copy the demo drafts or `assets/demo/` into a build's `_posts/` (`AGENTS.md`).

## What tests can't check

- **Visual criteria** (layout, spacing, how a page looks at phone width): write a stub so the criterion stays visible, and the EpicVerifier lists it for a manual check:

  ```python
  @pytest.mark.skip(reason="visual: AC4 -- tag chips wrap at 375 px without horizontal scroll")
  def test_story_3_tag_chips_wrap_on_phones():
      ...
  ```

- **Jekyll 3 compatibility:** tests run on local Jekyll 4, but GitHub Pages builds with Jekyll 3. A feature that only exists in Jekyll 4 passes here and breaks on setkus.lt.
