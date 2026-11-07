# Building and previewing setkus.lt by hand

For checks outside the test suite, such as chasing a failure that looks environmental or reviewing a page visually.

## Preview with drafts and demo content

```bash
JEKYLL_NO_BUNDLER_REQUIRE=true jekyll serve --config _config.yml,_config.dev.yml
```

Open http://localhost:4000/. Restart the server after editing either config file.

## Production build and demo check

Build the site the way GitHub Pages does, and check that it contains no demo content:

```bash
JEKYLL_ENV=production jekyll build && ls _site/assets/demo; ls -R _site/blog
```

Expected: the first `ls` reports that `_site/assets/demo` doesn't exist, and no demo post slug (`everything-a-post-can-do`, `sharing-ktor-client-kmp`) appears under `_site/blog/`. Anything else breaks the rules in `AGENTS.md`.

This is the check from `AGENTS.md`, written so it also works in zsh when there are no posts yet (zsh stops on an unmatched `_site/blog/*/` glob). The `test_baseline_production_has_no_demo_content` test runs the same check.

## Phone-width review

Tests can't check how a page looks. For each page a story changed, and each visual criterion:

1. Run the preview server above.
2. Open the page at 375 px wide: browser dev tools, or the built-in browser's mobile viewport.
3. Check that the page doesn't scroll sideways, code blocks scroll inside their box, text is readable, and nothing overlaps.
4. Check the same page at desktop width.

Record each check, its URL and the result in the epic's verification report.
