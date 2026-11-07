# PRD: Analytics

## Background

setkus.lt has no analytics today, so I can't tell how many people visit the site, which posts they read, or where they come from. I picked [counter.dev](https://counter.dev): it's free, doesn't use cookies, and collects only aggregate statistics (visits, pages, referrers, countries, devices). It needs one script tag on every page:

```html
<script src="https://cdn.counter.dev/script.js" data-id="cee64376-9fee-402d-98b4-58246fa7413a" data-utcoffset="2"></script>
```

The site has no theme and no plugins (`theme: null`), and its pages use three unrelated layouts that each write their own `<head>`:

- `_layouts/light.html`: `blog.html`, `resume.html`, and every post (through `_layouts/post.html`, which wraps `light`)
- `_layouts/default.html`: the home page, `index.html`
- `_layouts/page.html`: `privacy-policy.md` (`/torch-privacy-policy/`)

The script has to be added to all three by hand.

## Goals

- I can see visits to every HTML page of setkus.lt in my counter.dev dashboard.
- Only real visits to the live site are counted. Local previews (`jekyll serve`, with or without `_config.dev.yml`) and test builds with `JEKYLL_ENV` other than `production` load nothing from counter.dev.
- The counter.dev settings (site id and UTC offset) are kept in one place, so I can change them or turn analytics off without editing layouts.

## Non-goals

- Cookie banner or consent dialog. counter.dev sets no cookies and stores no personal data.
- A privacy policy for the website. The existing `/torch-privacy-policy/` page covers the Torch Android app only, and its text stays unchanged.
- Custom events, goals, click or scroll tracking.
- Showing visitor numbers on the site, or embedding the counter.dev dashboard.
- Counting Atom feed (`feed.xml`) readers.
- Any other analytics provider, or self-hosting `script.js`.

## Requirements

### Analytics settings in `_config.yml`

- Add an `analytics` section to `_config.yml`:

  ```yaml
  # counter.dev analytics. The script loads only in production builds.
  # Remove `id` to turn analytics off.
  analytics:
    counter_dev:
      id: "cee64376-9fee-402d-98b4-58246fa7413a"
      utcoffset: 2
  ```

- `_config.dev.yml` doesn't repeat or override this section. The script stays off locally because of the environment check below, not because of a different config.
- When `analytics.counter_dev.id` is missing or empty, no page contains the counter.dev script.

### Analytics include

- Create `_includes/analytics.html`. It outputs the counter.dev script tag only when both are true:
  - `jekyll.environment` is `production` (GitHub Pages sets this; a local `jekyll serve` uses `development`)
  - `site.analytics.counter_dev.id` is set
- The tag it outputs is exactly the snippet from counter.dev, with the values taken from the config:
  - `src="https://cdn.counter.dev/script.js"`
  - `data-id="{{ site.analytics.counter_dev.id }}"`
  - `data-utcoffset="{{ site.analytics.counter_dev.utcoffset }}"`
- No `async`, `defer` or other attributes are added, and the script isn't wrapped in other code.

### Script on every page

- Include `analytics.html` inside `<head>` in `_layouts/light.html`, `_layouts/default.html` and `_layouts/page.html`, as the last element before `</head>`.
- Don't include it in `_layouts/post.html`: posts already get it from `light.html`, and every page must contain the script exactly once.
- Pages affected in a production build: `/`, `/blog/`, `/resume/`, `/torch-privacy-policy/`, and every post under `/blog/<year>/<slug>/`.
- Nothing else changes in the built pages: same title, meta tags, stylesheets and content.
- `feed.xml` contains no script.

### Docs

- Add a short "Analytics" item to "How the site fits together" in `AGENTS.md`: where the settings live, that the script loads only in production, and that a new layout must include `analytics.html` in its `<head>`.

## Acceptance criteria (high level)

- In a production build (`JEKYLL_ENV=production`, `_config.yml` only), each of `/`, `/blog/`, `/resume/`, `/torch-privacy-policy/` and a post page has exactly one `<script>` with `src="https://cdn.counter.dev/script.js"`, inside `<head>`, with `data-id="cee64376-9fee-402d-98b4-58246fa7413a"` and `data-utcoffset="2"`.
- In a development build (`JEKYLL_ENV=development`, with `_config.yml,_config.dev.yml`), no page contains a `cdn.counter.dev` script, including demo drafts.
- In a production build whose config has no `analytics.counter_dev.id`, no page contains a `cdn.counter.dev` script.
- The built `feed.xml` doesn't contain `cdn.counter.dev`.
- Existing tests in `_tests/` still pass, and a production build prints no new Jekyll warnings.
- **Visual:** pages look exactly the same as before on desktop and at phone width.
- **Visual (after deploy):** opening setkus.lt in a browser shows a request to `cdn.counter.dev/script.js` in the network tab, and the visit appears in the counter.dev dashboard within a few minutes.

## Open questions for the ProductOwner

- **UTC offset.** Lithuania is UTC+2 in winter and UTC+3 in summer, but `data-utcoffset` is a fixed number. Keep `2` as counter.dev generated it, unless there's a reason to prefer `3`. My default: keep `2`.
- **Torch privacy policy page.** `/torch-privacy-policy/` says the Torch app doesn't track anyone. That statement is about the app, not the website, so the page gets the script like every other page. My default: track it. Flag it if you think excluding it is safer.
- **Script placement.** counter.dev's snippet has no `async` or `defer`. If loading it at the end of `<head>` blocks rendering noticeably, say so, but don't change the snippet without asking me.

## Phasing note

One epic. A sensible order:

1. Config section and `_includes/analytics.html` with the production check.
2. Include it in the three layouts (the testable change: one script per page in production, none in development).
3. `AGENTS.md` note.

Stories 2 and 3 depend on story 1. This could also be a single story.
