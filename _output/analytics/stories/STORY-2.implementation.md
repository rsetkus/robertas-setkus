# STORY-2 AC implementation map

Story: No counter.dev script outside production or without a site id.

Files changed: none. The two switches were written with STORY-1 in `_includes/analytics.html`,
and this story's tests confirm them. Line 9 holds both switches:

```liquid
{%- if jekyll.environment == "production" and counter_dev.id and counter_dev.id != "" -%}
```

- Environment switch: `jekyll.environment == "production"`. Without `JEKYLL_ENV`, Jekyll uses
  `development`, so `jekyll serve` and dev previews output nothing.
- Id switch: `counter_dev.id` is nil when the `analytics` section or the `id` key is missing
  (Liquid returns nil for a lookup on nil, so there is no build error), and `counter_dev.id != ""`
  rejects the empty string, which Liquid treats as truthy.

## AC8

Development build with `_config.yml,_config.dev.yml` (drafts included): no .html file contains cdn.counter.dev.

- _includes/analytics.html:9 `jekyll.environment == "production"` is false for `JEKYLL_ENV=development`, so the tag on line 10 is never output
- _includes/analytics.html:1 the explanatory comment uses `{%- comment -%}`, so the text "counter.dev" in it never reaches the HTML
- _layouts/light.html:21 the only analytics include on the `light`/`post` path (demo drafts render through `post` inside `light`), and it outputs nothing outside production
- _config.dev.yml:7 the dev config only turns on `show_drafts`/`unpublished` and sets `exclude`; it sets no analytics or environment value

## AC9

`_config.yml` only with `JEKYLL_ENV=development` (plain `jekyll serve`): no .html file contains cdn.counter.dev.

- _includes/analytics.html:9 the environment check fails in `development`, although `_config.yml` sets an id
- _config.yml:36 the `analytics` section is present with a real id, so the environment check alone keeps the script out
- _layouts/default.html:9, _layouts/light.html:21 and _layouts/page.html:26 are the only call sites, and each goes through this guard

## AC10

Production build of a `_config.yml` without an `analytics` section: the build succeeds and has no cdn.counter.dev.

- _includes/analytics.html:8 `site.analytics.counter_dev` is nil when the section is missing; Liquid does not raise on a nil lookup, so the build succeeds
- _includes/analytics.html:9 `counter_dev.id` is nil, so the `and` chain is false and line 10 is not output

## AC11

Production build with `counter_dev` but no `id` key, and one with `id: ""`: no cdn.counter.dev in either build.

- _includes/analytics.html:9 `counter_dev.id` (truthiness) is false for a missing key (nil)
- _includes/analytics.html:9 `counter_dev.id != ""` is false for the empty string, which is truthy in Liquid and would otherwise pass the first check
- _includes/analytics.html:4 the header comment states that the id must be "set and not empty"

## AC12

`_config.dev.yml` loaded as YAML has no `analytics` key.

- _config.dev.yml:7 the file's keys are `show_drafts`, `unpublished` (line 8) and `exclude` (line 9) only; it does not repeat or override `analytics`
- _config.yml:36 `analytics` is set only in the production config, and local builds have no script because of the environment check (_includes/analytics.html:9)
