# Rules for agents

This is the Jekyll site for setkus.lt. GitHub Pages builds it from `main` using only `_config.yml`, so anything Jekyll outputs from `main` goes live.

## Demo content: never publish it on setkus.lt

Demo posts exist to preview the blog's design. They may live in the repository, but Jekyll must never output them for production:

- `_drafts/everything-a-post-can-do.md`
- `_drafts/sharing-ktor-client-kmp.md`
- images and videos in `assets/demo/`

1. Demo posts stay in `_drafts/` and always keep both `demo: true` and `published: false` in their front matter. GitHub Pages builds neither drafts nor unpublished posts.
2. Demo images, videos and other files go only in `assets/demo/`. Never remove `assets/demo/` from `exclude` in `_config.yml`.
3. Never move a demo post to `_posts/`, never link to demo content from real pages, and never copy demo files elsewhere under `assets/`.
4. New demo content follows the same rules: a draft with `demo: true` and `published: false`, and its files in `assets/demo/<slug>/`.
5. Never bypass the pre-push guard (`git push --no-verify`) or weaken it.

If a request would break one of these rules, stop and ask the user first, even if the request seems to require it.

## Previewing locally

`_config.dev.yml` turns on drafts and unpublished posts and serves `assets/demo/`. It's for local use only:

```bash
JEKYLL_NO_BUNDLER_REQUIRE=true jekyll serve --config _config.yml,_config.dev.yml
```

Before pushing a change that touches demo content, check that a production build contains none of it:

```bash
JEKYLL_ENV=production jekyll build && ls _site/assets/demo _site/blog/*/ 2>&1
```

## Pre-push guard

`.githooks/pre-push` refuses a push when `_config.yml` stops excluding `assets/demo/`, when a `demo: true` post lacks `published: false`, or when a demo post is in `_posts/`. Install it once per clone (it covers every worktree):

```bash
cp .githooks/pre-push "$(git rev-parse --git-common-dir)/hooks/pre-push"
```

## Writing posts

Formats, templates and the writing guide are in `_templates/README.md`.

## Build and check

There are no tests or linters. The check is a clean production build: run the build command under "Previewing locally" and read Jekyll's warnings. Restart `jekyll serve` after editing either config file, because it doesn't reload them.

Locally `jekyll -v` is 4.x, but GitHub Pages builds with Jekyll 3 and its whitelisted plugins only. Don't rely on Jekyll 4-only features or add plugins to the `Gemfile` expecting them to run on setkus.lt.

## How the site fits together

- **No theme, no plugins.** `theme: null`. Things a plugin would normally do are written by hand: `feed.xml` is a Liquid Atom template, the SEO and Open Graph tags live in `_layouts/light.html`, and reading time comes from `_includes/reading-time.html`.
- **Three unrelated layouts, each with its own CSS:**
  - `light` is the current design (`assets/css/light.css`). `blog.html`, `resume.html` and every post (`post` → `light`) use it. `assets/css/syntax.css` loads only on posts.
  - `default` is the older home page design (`index.html`, `assets/css/style.css`, background image, `_includes/nav.html`).
  - `page` is self-contained with inline styles (`privacy-policy.md`).
- **Posts:** the `defaults` in `_config.yml` give every post `layout: post` and the permalink `/blog/:year/:title/`. Formats, front matter and post includes (`figure.html`, `youtube.html`) are documented in `_templates/README.md`.
- **Résumé:** `/resume/` is rendered from `_data/experience.yml` (field rules are in its header comment). Company logos go in `assets/images/companies/`.
- **Two configs with duplicated `exclude` lists.** When configs are merged, arrays replace each other, and Jekyll 3 replaces its default exclude list too. So `_config.dev.yml` repeats the whole production list minus `assets/demo/`. When you add an entry to `exclude` in `_config.yml`, add it to `_config.dev.yml` as well.
