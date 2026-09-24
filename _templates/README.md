# Writing guide

How to write posts for [setkus.lt/blog](https://setkus.lt/blog/). Jekyll skips folders that start with `_`, so nothing in `_templates/` is published.

## Workflow

```bash
mkdir -p _drafts
cp _templates/deep-dive.md _drafts/sharing-ktor-client-with-kmp.md   # or til.md, talk-recap.md
JEKYLL_NO_BUNDLER_REQUIRE=true jekyll serve --drafts                   # preview at http://localhost:4000/blog/
git mv _drafts/sharing-ktor-client-with-kmp.md _posts/2026-10-01-sharing-ktor-client-with-kmp.md
```

- The file name is the URL: `_posts/2026-10-01-sharing-ktor-client-with-kmp.md` → `/blog/2026/sharing-ktor-client-with-kmp/`. Keep slugs short, lowercase and hyphenated, and don't rename them after publishing.
- Jekyll never publishes `_drafts/`, but anything you commit there is still visible in the GitHub repo.
- `JEKYLL_NO_BUNDLER_REQUIRE=true` is only needed while `bundle install` is broken locally. Otherwise use `bundle exec jekyll serve --drafts`.

## Pick a format

| Format | Template | Length | Use it for |
|---|---|---|---|
| Deep dive / how-to | `deep-dive.md` | 800–1,500 words | A problem you solved, end to end, with code the reader can reuse. |
| TIL | `til.md` | 150–400 words | One small finding: a Gradle flag, a coroutine gotcha, an IDE trick. |
| Talk recap | `talk-recap.md` | 400–800 words | A talk you gave or watched, e.g. at Vilnius Kotlin User Group. |

One idea per post. If a deep dive needs two "and"s in its title, it's two posts.

## Front matter

```yaml
---
title: "Sharing a Ktor client between Android and iOS"   # sentence case, ≤ 70 characters
description: "Set up one Ktor client in commonMain, with engines per platform and tests that run on both."   # one sentence, ≤ 160 characters
tags: [kmp, kotlin]
image: /assets/images/posts/sharing-ktor-client/cover.jpg   # optional cover, also the link preview
image_alt: "Diagram of one Ktor client shared by Android and iOS"
updated: 2026-11-02   # optional; add when you change a published post
---
```

- **Title:** say what the reader gets, not a pun. "Faster Gradle builds with configuration cache", not "Need for speed".
- **Description:** shown on the blog index, in the feed and in search results. Write it for someone deciding whether to click.
- **Tags:** 1–3, lowercase, from this list, so they stay useful: `kotlin` `android` `kmp` `compose` `gradle` `coroutines` `testing` `architecture` `til` `talks`. Add a new tag only when a second post will use it.
- The date comes from the file name. Don't add `date:` unless you need a time of day.

## Structure

- **Open with the payoff.** The first 2–3 sentences say the problem, who the post is for and what they'll have at the end. Readers decide in 10 seconds.
- **Say what you tested with,** e.g. `Tested with: Kotlin 2.2, AGP 8.12, Compose BOM 2026.09`. Android posts age fast; versions tell future readers whether the post still applies.
- **Use `##` for sections and `###` sparingly.** The layout already renders the title as the page's `<h1>`, so never use `#` in the body.
- **End with takeaways** (three bullets) and a link to runnable code where there is some.

## Voice

- First person, direct, active voice: "I moved the cache to `commonMain`", not "The cache was moved".
- Explain *why* before *how*. The reasoning is what readers can't get from the docs.
- Keep paragraphs to 4 sentences or fewer. Break walls of text with a list, a code block or a subheading.
- Spell out acronyms on first use: "Kotlin Multiplatform (KMP)".
- Drop "simply", "just", "easy" and "obviously". If it were obvious, the reader wouldn't be here.
- Use American spelling ("optimize", "behavior") to match the Kotlin and Android docs.
- Show real numbers when you claim an improvement: "build time went from 94 s to 31 s", not "much faster".

## Code

- Always name the language after the opening fence so it gets highlighted: `kotlin` (also for `.gradle.kts`), `toml`, `bash`, `xml`, `yaml`, `swift`, `diff`.
- Start each block with a comment giving the file path, so readers know where it goes:

  ```kotlin
  // shared/src/commonMain/kotlin/lt/setkus/api/ApiClient.kt
  class ApiClient(private val http: HttpClient) {
      suspend fun items(): List<Item> = http.get("items").body()
  }
  ```

- Keep blocks to about 25 lines. Leave out imports and boilerplate unless they're the point.
- Wrap lines at about 70 characters. That's what fits in the column on desktop; longer lines scroll sideways.
- Only show code that compiles. Copy it from a working project, not from memory.
- Use a `diff` block to show a change to existing code:

  ```diff
  -    implementation("io.ktor:ktor-client-okhttp:2.3.12")
  +    implementation(libs.ktor.client.okhttp)
  ```

- Put one sentence before each block saying what it does. Never place two code blocks back to back without text between them.
- Use inline `code` for identifiers, file names and Gradle tasks: `./gradlew :shared:allTests`.
- Jekyll treats `{{ … }}` and `{% … %}` as template tags. Wrap blocks that contain them (GitHub Actions `${{ secrets.TOKEN }}`, for example) in `{% raw %}` … `{% endraw %}`.

## Images, video and embeds

The demo post `_drafts/everything-a-post-can-do.md` shows every option rendered, with the Markdown under each one. It lives only on the local `debug` branch and must never be published (see `AGENTS.md`). To view it, run `git switch debug` and `jekyll serve --drafts --unpublished`, then open `/blog/2026/everything-a-post-can-do/`. In short:

- Put files in `assets/images/posts/<slug>/`. Always write alt text that says what the image shows, not "screenshot".
- **Plain image:** `![Alt text](/assets/images/posts/slug/file.png)`. Add `{: .bordered}` after it for a thin frame.
- **Caption, phone screenshot, wide screenshot, recording:** use the figure include:

  ```liquid
  {% include figure.html src="/assets/images/posts/slug/screen.webp"
     alt="What it shows" caption="Optional, Markdown allowed"
     class="phone" width="600" height="1334" %}
  ```

  - `class="phone"` for phone screenshots (280 px wide), `class="wide"` for large screenshots (up to 960 px on desktop), `class="bordered"` for a frame. Wrap several figures in `<div class="gallery">` to show them side by side.
  - `link=true` opens the full-size image on click. `width`/`height` are the file's pixel size and stop the page jumping while it loads.
  - An `.mp4` in `src` plays like a GIF (autoplay, muted, looped). Add `poster=` for the frame shown before it plays, and optionally `webm=` for a second copy.
- **YouTube:** `{% include youtube.html id="VIDEO_ID" title="Talk title" %}`.
- **Formats and sizes:** phone screenshots as WebP or PNG at 600 px wide, desktop screenshots up to 1,600 px, diagrams as SVG drawn about 440 px wide with text of 14 px or more (wider ones shrink on phones until they're unreadable), recordings as MP4 at 600 px, and a cover at 1,200 × 630 px JPEG.
- **Capture** straight from the emulator or simulator: `adb exec-out screencap -p > screen.png` and `xcrun simctl io booted screenshot screen.png`. **Shrink** with `cwebp -q 82 -resize 600 0 screen.png -o screen.webp`.

## Callouts and links

- **Callouts:** a blockquote with a bold label, then a class line: `.note` (blue), `.tip` (green) or `.warning` (amber). Keep them rare, one or two per post.

  ```markdown
  > **Warning:** A leading slash in the request path drops the base URL's path.
  {: .warning}
  ```

- **Links:** make the link text say where it goes: "the [Ktor client engines docs](https://ktor.io/docs/client-engines.html)", never "click [here](…)". Link to specific versions of docs or source when the details matter.
- **More:** footnotes (`[^1]`), abbreviations (`*[KMP]: Kotlin Multiplatform`), task lists, definition lists, keyboard keys (`<kbd>`), a table of contents (`* TOC` + `{:toc}`), collapsible blocks (`<details markdown="1">`) and line-numbered code are all in the demo draft.

## Before publishing

- [ ] Title and description say what the reader gets
- [ ] 1–3 tags from the list
- [ ] "Tested with" versions (deep dives)
- [ ] Every code block has a language and a file path, and compiles
- [ ] All links open, and images have alt text
- [ ] Previewed at phone width (code blocks scroll, and the page doesn't scroll sideways)
- [ ] Read it aloud once: cut anything you'd skip when speaking
