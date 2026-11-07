# Verification: EPIC-1

Verified at: 2026-11-08T00:00:00Z (session date; local run)
Verifier: EpicVerifier-EPIC-1
Stories in scope: STORY-1, STORY-2, STORY-3, STORY-4

## Preconditions
- All stories DONE: yes (`verify_epic.py --feature analytics --epic EPIC-1`: `all_done: true`, `non_done: {}`)
- All AC implementation maps verified: yes (`ac_maps_verified: true`, `failed_stories: []`)

## Cross-story regression
- Test selector: full suite, `python -m pytest _tests/ -v --tb=short` (per `_docs/testing.md`; includes `test_baseline_*`)
- Tests collected: 63
- Tests passed: 61
- Tests skipped: 2 (the STORY-3 `visual:` stubs for AC15 and AC16, see Manual checks)
- Tests failed: 0

## Production demo check (AGENTS.md)
Command: `JEKYLL_ENV=production jekyll build --destination <scratchpad>/prod-site` (scratch destination, `_site/` untouched).

- Build exit code: 0. Output has no `Warning` / `Deprecation` / error lines.
- `assets/demo`: does not exist in the build ("No such file or directory").
- `blog/`: contains only `index.html`. No `everything-a-post-can-do` or `sharing-ktor-client-kmp` slug, and no file in the build mentions either slug.
- No `AGENTS.md` / `AGENTS.html` in the build.
- Result: PASS. No demo content in production.

## Epic acceptance
Full suite (`python -m pytest _tests/ -v --tb=short`) passes, including test_baseline_*
(no demo content in production). In the production build every built .html file contains
cdn.counter.dev exactly once and feed.xml contains it zero times; in the dev build
(_config.yml,_config.dev.yml) no file contains it. Manual checks: the visual criteria of STORY-3.

Satisfied: yes (manual checks pending, listed below)

Notes:
- Full suite: 61 passed, 2 skipped (visual stubs), 0 failed; all 18 `test_baseline_*` cases passed.
- Production build (real site, no fixture posts), counted by hand with `grep -o cdn.counter.dev`:
  `index.html` 1, `blog/index.html` 1, `resume/index.html` 1, `torch-privacy-policy/index.html` 1;
  `feed.xml` 0. Post pages are covered by `fixture_site` in `test_story_1_every_html_file_has_counter_once`.
- Dev build (`--config _config.yml,_config.dev.yml`, scratch destination): 0 files contain
  `cdn.counter.dev`, including both demo draft pages (`blog/2026/everything-a-post-can-do/`,
  `blog/2026/sharing-ktor-client-kmp/`).

## Epic-level checks beyond per-story criteria
- **Layout coverage:** `_layouts/` has four layouts. `default.html:9`, `light.html:21` and `page.html:26`
  include `analytics.html` as the last line of `<head>`; `post.html` has no `<head>` and wraps `light`
  (front matter `layout: light`), so posts get the script once.
- **Jekyll 3 compatibility:** `_includes/analytics.html` uses `assign`, `if ... and ... != ""` and
  `{%- -%}` whitespace control. All are supported by Liquid 4, which GitHub Pages' Jekyll 3 uses. No plugins.
- **Demo rules:** the diff changes no `exclude` list in `_config.yml` or `_config.dev.yml`; no demo file is
  moved, linked or copied. `_config.dev.yml` has no `analytics` key.
- **Changed files:** `AGENTS.md`, `_config.yml`, `_docs/testing.md`, `_layouts/{default,light,page}.html`,
  `_tests/conftest.py`, `_tests/requirements.txt` (adds `pyyaml>=6.0`); new `_includes/analytics.html`,
  `_prds/analytics.md`, `_tests/test_analytics.py`, `_tests/test_agents_md.py`, `_output/analytics/`.

## Manual checks for the User
Not done by the verifier (no visual review was run). The only change to built pages is one `<script>` at the end of `<head>`. It renders nothing, and AC13 shows `<head>` and `<body>` are otherwise identical to a build with analytics off. Still, check by eye:

1. **AC15, visual, before merge.** Run `JEKYLL_NO_BUNDLER_REQUIRE=true jekyll serve --config _config.yml,_config.dev.yml`.
   Note that the preview is a development build, so the script is not loaded there (by design).
   Open each page at desktop width and at 375 px (`_docs/build_run.md`, "Phone-width review"):
   - http://localhost:4000/ (`default` layout)
   - http://localhost:4000/blog/ (`light`)
   - http://localhost:4000/resume/ (`light`)
   - http://localhost:4000/torch-privacy-policy/ (`page`)
   - a post, e.g. http://localhost:4000/blog/2026/everything-a-post-can-do/ (demo draft, preview only; `post` in `light`)

   Check: each page looks the same as before the change, with no shift, gap or extra element and no sideways scroll at 375 px.
   To see the page with the script present, open a production build (`JEKYLL_ENV=production jekyll build`) from a local static server. It should look the same.
2. **AC16, visual, after deploy.** Open https://setkus.lt/ with the browser's network tab open. Check that
   `https://cdn.counter.dev/script.js` is requested, and that the visit shows in the counter.dev dashboard within a few minutes.

## Epic status flip: resolved, EPIC-1 is VERIFIED
- First attempt refused: `update_epic_status.py EPIC-1 VERIFIED` returned
  `{"success": false, "error": "invalid transition TODO -> VERIFIED for EPIC-1 (allowed: ['BLOCKED', 'IN_PROGRESS'])"}`.
  The epic YAML was still `status: TODO`, and nothing in the run had moved it through `IN_PROGRESS -> DONE`.
- Resolved: the orchestrator moved EPIC-1 `TODO -> IN_PROGRESS -> DONE` with `update_epic_status.py`.
- Re-checked before the flip: EPIC-1.yaml `status: DONE`. The working-tree diff is the same as in the first run.
  `verify_epic.py` succeeded again (`all_done: true`, `ac_maps_verified: true`). Full suite re-run: 61 passed, 2 skipped, 0 failed.
- Flip: `update_epic_status.py EPIC-1 VERIFIED --epics-dir _output/analytics/epics` returned
  `{"success": true, "old_status": "DONE", "new_status": "VERIFIED"}`.

## Other notes for the reviewer
- **Parser-blocking script (spec flag, User kept the default):** the snippet has no `defer`/`async`, so first paint
  waits for `cdn.counter.dev/script.js`. If counter.dev's CDN is slow or down, pages render late. Adding `defer` is a possible one-word follow-up.
- **Torch privacy page is tracked (spec flag, User kept the default):** `/torch-privacy-policy/` says the app
  "doesn't track anyone" while the page itself now loads a counter. That statement is accurate (it is about the app), but a reader could take it the other way.
- `_tests/requirements.txt` now needs PyYAML. Re-run the one-time `pip install` in other environments.
- Nothing has been committed. The pre-push guard was not run, because this verification did no push.
