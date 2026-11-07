# Feature: analytics

PRD: `_prds/analytics.md` (the user's requirements; this spec does not replace it).

## Overview

setkus.lt gets cookieless, aggregate visitor analytics from counter.dev. One script tag,
exactly as counter.dev generates it, is placed at the end of `<head>` on every HTML page of a
production build. The site id and UTC offset live in one `analytics` section of `_config.yml`.
The script is output only when `jekyll.environment` is `production` and a site id is set, so local
previews, development builds and any build without an id load nothing from counter.dev. A short
"Analytics" note is added to `AGENTS.md`.

## Requirements

### Settings (`_config.yml`)
- `_config.yml` gains the `analytics` section from the PRD, with its two comment lines:
  `analytics.counter_dev.id: "cee64376-9fee-402d-98b4-58246fa7413a"` and
  `analytics.counter_dev.utcoffset: 2`.
- `_config.dev.yml` does not repeat or override `analytics`. The script is off locally because of
  the environment check, not because of a different config.
- When `analytics.counter_dev.id` is missing, null or an empty string, no page contains the script.

### Include (`_includes/analytics.html`)
- Outputs the counter.dev script tag only when both are true:
  - `jekyll.environment == "production"`
  - `site.analytics.counter_dev.id` is set and not empty
- The tag is counter.dev's snippet with the config values substituted:
  `<script src="https://cdn.counter.dev/script.js" data-id="{{ site.analytics.counter_dev.id }}" data-utcoffset="{{ site.analytics.counter_dev.utcoffset }}"></script>`
- No `async`, `defer`, `type` or other attributes; no wrapper code; no inline script content.

### Layouts
- `_layouts/light.html`, `_layouts/default.html` and `_layouts/page.html` include
  `analytics.html` as the last element inside `<head>`.
- `_layouts/post.html` does not include it (posts get it through `light`). Every HTML page
  contains the script exactly once.
- Pages affected in production: `/`, `/blog/`, `/resume/`, `/torch-privacy-policy/` and every post
  at `/blog/<year>/<slug>/`.
- Apart from the script, built pages are unchanged: same title, meta tags, stylesheets, inline
  styles and body content.
- `feed.xml` contains no script.

### Docs
- `AGENTS.md`, section "How the site fits together", gets a short "Analytics" item: settings live in
  `_config.yml` under `analytics.counter_dev`, the script loads only in production builds, and a new
  layout must include `analytics.html` in its `<head>`.

### Open questions from the PRD (resolved)
- The User approved the spec on 2026-11-08 and kept all three defaults below.
- **UTC offset: keep `2`.** It is what counter.dev generated for this site, and the offset only
  moves the dashboard's day boundary by one hour in summer; a fixed value can't follow DST anyway.
- **Torch privacy policy page: track it.** Its text is about the Torch app, not the website, and
  counter.dev sets no cookies and stores no personal data. Flag for the User: the page states the
  app "doesn't track anyone" while the page itself now loads a counter. This is accurate, but a
  reader (or a Play Store reviewer) might read it the other way. The page text stays unchanged
  (PRD non-goal); if the User prefers, excluding this one page is a small follow-up.
- **Script placement: keep the snippet as is (no `async`/`defer`).** Flag for the User: a plain
  external `<script>` in `<head>` is parser-blocking, so first paint waits until
  `cdn.counter.dev/script.js` downloads. The file is small and the pages already block on Google
  Fonts stylesheets, so the cost is normally negligible, but if counter.dev's CDN is slow or down,
  every page renders late until the request fails. Adding `defer` would remove that risk; per the
  PRD this is not changed without the User's go-ahead.

## Edge Cases
- **Plain `jekyll serve` / `jekyll build` with `_config.yml` only:** `JEKYLL_ENV` is unset, so
  Jekyll uses `development` and no script is output.
- **Dev preview with drafts:** `_config.yml,_config.dev.yml` builds include the demo drafts
  (`_drafts/`). Those pages must not contain the script either.
- **Empty string id:** in Liquid an empty string is truthy, so `{% if site.analytics.counter_dev.id %}`
  alone is not enough; `id: ""` must also turn analytics off.
- **No `analytics` section at all:** the build must still succeed (no Liquid error) and output no
  script.
- **Posts:** a post renders `post` inside `light`; the script must appear once, not twice.
- **`feed.xml`** uses `layout: null` and must stay script-free.
- **Missing `utcoffset` with an id set:** not required by the PRD; the shipped config always sets
  it. No criterion covers this case.
- **A future page with no layout** (or a new layout) gets no script unless the layout includes
  `analytics.html`; the `AGENTS.md` note covers this.

## Technical Notes
- GitHub Pages builds with Jekyll 3 and sets `JEKYLL_ENV=production`; local Jekyll is 4.x. The
  include must use only Liquid that Jekyll 3 supports. No plugins (`theme: null`).
- Demo-content rules in `AGENTS.md` are untouched: no demo files are moved, linked or copied, and
  `assets/demo/` stays excluded. This feature changes no `exclude` list.
- `_posts/` is empty in the repo today, so post-page criteria are checked with `fixture_site`
  (`_tests/fixtures/posts/2026-01-15-fixture-post.md`, built at `/blog/2026/fixture-post/`).
- Several criteria need builds the current `_tests/conftest.py` `build()` helper can't make: a
  production build with a changed or missing `analytics` section, and a `development` build with
  `_config.yml` only. Jekyll deep-merges hashes across `--config` files, so an override file works
  for changed or empty values, but removing the section needs an edited copy of `_config.yml`.
  The TestCreator may extend `build()` for this, keeping its temp-copy design (`_docs/testing.md`).
- The "no new Jekyll warnings" criterion needs the build's stdout/stderr; a production build prints
  no warnings today, so any warning line is new.
- Tests assert on built HTML (BeautifulSoup), never on Liquid source. The `_config.dev.yml` and
  `AGENTS.md` criteria are the exceptions, because they are about those files themselves.
- Test names follow `test_story_<N>_<what>`.

## Future considerations (out of scope, from the PRD's Non-goals)
- Cookie banner or consent dialog.
- A privacy policy for the website; any change to the `/torch-privacy-policy/` text.
- Custom events, goals, click or scroll tracking.
- Showing visitor numbers on the site or embedding the counter.dev dashboard.
- Counting Atom feed readers.
- Other analytics providers, or self-hosting `script.js`.
- Possible follow-ups the User may choose: `defer` on the script; excluding the Torch privacy page.
