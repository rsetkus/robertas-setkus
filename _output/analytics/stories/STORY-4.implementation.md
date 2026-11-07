# STORY-4 AC implementation map

Story: AGENTS.md documents analytics.

Files changed:
- `AGENTS.md` (new "Analytics" bullet at the end of "How the site fits together", line 63)

## AC17

The "How the site fits together" section has a bullet starting with **Analytics** that mentions
_config.yml and analytics.counter_dev, says the script loads only in production, and says a new
layout must include analytics.html in its `<head>`.

- AGENTS.md:53 the "## How the site fits together" heading; the section runs to "## Running Sage" (AGENTS.md:65)
- AGENTS.md:63 bullet starting with `**Analytics.**`: settings live in `_config.yml` under `analytics.counter_dev`
- AGENTS.md:63 says `_includes/analytics.html` outputs the script only in production builds and only when `id` is set
- AGENTS.md:63 says a new layout must include `analytics.html` in its `<head>` (layouts that wrap `light`, like `post`, get it already)

## AC18

The production build contains no AGENTS.md or AGENTS.html.

- _config.yml:66 `AGENTS.md` is in `exclude`, so the production build never copies or renders it; the edit adds no front matter and changes no config
- _config.dev.yml:10 the dev config repeats the `AGENTS.md` exclude, so preview builds don't publish it either
