# STORY-3 AC implementation map

Story: Pages are otherwise unchanged.

Files changed: none. STORY-1 made all the changes this story guards. Its whole diff to the
layouts is one `{% include analytics.html %}` line in each of the three layouts (`git diff --stat`:
`_layouts/default.html`, `_layouts/light.html`, `_layouts/page.html` +1 line each; `_config.yml`
+7 lines for the `analytics` section). No title, meta, link, style or body markup was touched.
The include outputs exactly one `<script>` element and nothing else: its comment uses
`{%- comment -%}` and every tag trims whitespace (`{%-`/`-%}`), so it adds no text node either.

Tests: `python -m pytest _tests/ -k "story_3_" -v` gives 6 passed and 2 skipped (AC15 and AC16 are
visual stubs). Full suite: 61 passed, 2 skipped.

## AC13

The five pages built with the shipped config and with no `analytics.counter_dev.id` have the same `<head>` and `<body>` once the counter.dev script is removed.

- _includes/analytics.html:10 the only element the include can output: one `<script src="https://cdn.counter.dev/script.js" ...>`, which the test removes. With no id, line 9 is false and the include outputs nothing
- _includes/analytics.html:1 the explanatory comment is a `{%- comment -%}` block, so none of its text reaches the page
- _includes/analytics.html:8 `counter_dev` is assigned with whitespace-trimming tags, so the include adds no stray text in either build
- _layouts/light.html:21 the only line added to `light` (used by `/blog/`, `/resume/` and posts), placed after the feed `<link>` and before `</head>`; lines 4-20 and the `<body>` (line 23 on) are unchanged
- _layouts/default.html:9 the only line added to `default` (`/`), after the Google Fonts `<link>`; the `<body>` (line 11 on) is unchanged
- _layouts/page.html:26 the only line added to `page` (`/torch-privacy-policy/`), after the inline `</style>`; the `<body>` (line 28 on) is unchanged
- _config.yml:36 the `analytics` section is a new top-level key that no other template reads, so it changes nothing else in the build

## AC14

A production build with `_config.yml` only and the fixture posts exits 0 and prints no Warning or Deprecation line.

- _includes/analytics.html:9 `counter_dev.id` is read through `site.analytics.counter_dev` (line 8); on Jekyll 3 and 4 a nil lookup is silent, so the include raises no Liquid warning even without the section
- _includes/analytics.html:9 the condition uses only `==`, `!=` and `and`, which Jekyll 3 and 4 Liquid both support without a deprecation notice
- _config.yml:36 the new section is plain YAML (one mapping, a quoted string id and an integer offset), so config parsing adds no warning
- _layouts/light.html:21 the include is called with the plain `{% include analytics.html %}` form, with no parameters, so Jekyll prints no include warning

## AC15

Visual: the five pages look the same at desktop width and at 375 px. Needs the User's manual check (the test is a skip stub).

- _includes/analytics.html:10 the include adds only a `<script>` element inside `<head>`; a script element has `display: none` in every browser, takes no space and has no style, so it cannot shift or add a gap to the layout
- _layouts/light.html:21 the script sits in `<head>` after every stylesheet `<link>` (lines 17-20), so the CSS cascade and its order are unchanged
- _layouts/default.html:9 likewise after `style.css` and the Google Fonts link (lines 7-8)
- _layouts/page.html:26 likewise after the inline `<style>` block that ends on line 25
- _includes/analytics.html:10 counter.dev's `script.js` only sends a page-view request and inserts no visible element (spec: "no wrapper code; no inline script content")

## AC16

Visual (after deploy): https://setkus.lt/ requests cdn.counter.dev/script.js and the visit shows in the counter.dev dashboard. Needs the User's manual check after the merge to `main`.

- _includes/analytics.html:9 GitHub Pages builds with `JEKYLL_ENV=production`, so the environment check passes on setkus.lt
- _config.yml:38 `id: "cee64376-9fee-402d-98b4-58246fa7413a"` is the site id counter.dev generated for setkus.lt, so the dashboard receives the visit
- _config.yml:39 `utcoffset: 2` is passed as `data-utcoffset`
- _includes/analytics.html:10 the tag loads `https://cdn.counter.dev/script.js` with `data-id` and `data-utcoffset`, which is the request seen in the network tab
- _layouts/default.html:9 `/` uses the `default` layout, so the home page outputs the script
