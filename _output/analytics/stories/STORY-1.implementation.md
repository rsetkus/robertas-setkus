# STORY-1 AC implementation map

Story: The counter.dev script is in the head of every production page.

Files changed:
- `_config.yml` (new `analytics.counter_dev` section, lines 34-39)
- `_includes/analytics.html` (new include)
- `_layouts/light.html`, `_layouts/default.html`, `_layouts/page.html` (include as last element of `<head>`)
- `_layouts/post.html` is unchanged: posts render `post` inside `light`, so they get the script once.

Pages and their layouts: `index.html` uses `default`; `blog.html` and `resume.html` use `light`;
`privacy-policy.md` (`/torch-privacy-policy/`) uses `page`; posts use `post` inside `light`.

## AC1

Exactly one counter.dev script, inside `<head>`, on the five production pages.

- _includes/analytics.html:9 `counter_dev` guard: output only when `jekyll.environment == "production"` and the id is set and not empty
- _includes/analytics.html:10 the `<script src="https://cdn.counter.dev/script.js" ...>` tag
- _layouts/light.html:21 include inside `<head>` (`/blog/`, `/resume/`, every post)
- _layouts/default.html:9 include inside `<head>` (`/`)
- _layouts/page.html:26 include inside `<head>` (`/torch-privacy-policy/`)
- _layouts/post.html has no include, so a post page contains the script once (through `light`)

## AC2

`data-id` and `data-utcoffset` come from `_config.yml`.

- _config.yml:36 `analytics` section with `counter_dev.id: "cee64376-9fee-402d-98b4-58246fa7413a"` and `utcoffset: 2`
- _includes/analytics.html:8 `counter_dev` is assigned from `site.analytics.counter_dev`
- _includes/analytics.html:10 `data-id="{{ counter_dev.id }}"` and `data-utcoffset="{{ counter_dev.utcoffset }}"`

## AC3

Exactly the three attributes src, data-id and data-utcoffset; no async or type attribute and no other loading attribute; no text content.

- _includes/analytics.html:10 the tag is counter.dev's snippet verbatim with only src, data-id and data-utcoffset, and an empty body (`<script ...></script>`)

## AC4

The script is the last element child of `<head>`.

- _layouts/light.html:21 include is the line directly before `</head>` (line 22)
- _layouts/default.html:9 include is the line directly before `</head>` (line 10)
- _layouts/page.html:26 include is the line directly before `</head>` (line 27), after the inline `<style>`

## AC5

Every built .html file mentions cdn.counter.dev exactly once.

- _layouts/light.html:21 the only include on the `light` path; `post` adds none
- _layouts/default.html:9 the only include on the `default` path
- _layouts/page.html:26 the only include on the `page` path
- _includes/analytics.html:10 the include outputs cdn.counter.dev once and the comment block (lines 1-7) uses `{%- comment -%}`, so no other mention reaches the HTML

## AC6

`feed.xml` contains no script and no cdn.counter.dev.

- feed.xml:2 `layout: null`, so no layout (and no analytics include) wraps the feed
- _includes/analytics.html:10 the script exists only in this include, which `feed.xml` never includes

## AC7

Values follow the config: a build overriding `analytics.counter_dev.id` and `utcoffset` gets those values.

- _includes/analytics.html:8 `counter_dev` reads `site.analytics.counter_dev` at build time; the layouts contain no literal id or offset
- _includes/analytics.html:10 `data-id` and `data-utcoffset` are Liquid output of the config values
- _config.yml:36 the shipped defaults, which an extra `--config` file overrides through Jekyll's hash deep-merge
