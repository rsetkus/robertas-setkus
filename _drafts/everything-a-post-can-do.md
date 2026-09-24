---
demo: true       # demo only, never publish (see AGENTS.md)
published: false
title: "Everything a post can do"
description: "A tour of every element the blog supports, from screenshots and screen recordings to callouts and code, each with the Markdown that makes it."
tags: [android, kmp]
image: /assets/demo/everything-a-post-can-do/cover.jpg
image_alt: "Title card reading Everything a post can do, next to a short Kotlin snippet"
updated: 2026-09-24
---

> **Reference post:** this draft shows what a post can contain. Each section shows the result first. Open **Markdown** below it to see what to type.
{: .note}

* TOC
{:toc}

## Images

Keep a post's images in `assets/images/posts/<slug>/`, named after what they show. There are two ways to add one: a plain Markdown image, or the `figure` include when you need a caption or a layout option.

### Plain Markdown image

The quickest option. The image is centered and never wider than the column. This one is an SVG diagram, which stays sharp at any size.

![Diagram: commonMain holds ItemsApi and createHttpClient; androidMain provides the OkHttp engine and iosMain the Darwin engine](/assets/demo/everything-a-post-can-do/source-sets.svg)

<details markdown="1"><summary>Markdown</summary>

```markdown
![Diagram: commonMain holds ItemsApi and createHttpClient; …](/assets/images/posts/slug/source-sets.svg)
```

Add a class or attributes in `{: }` straight after the image, e.g. `{: .bordered width="400"}`. `.bordered` adds a thin frame, for screenshots with white edges.
</details>

### Figure with a caption

The `figure` include adds a caption, which can contain Markdown. `link=true` makes the image open at full size when clicked. Try it on this one.

{% include figure.html src="/assets/demo/everything-a-post-can-do/test-run.png" alt="Terminal showing the shared tests passing on the JVM and the iOS simulator" caption="Shared tests passing on both targets. Click to open full size." link=true width="1600" height="700" %}

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
{% include figure.html
   src="/assets/images/posts/slug/test-run.png"
   alt="Terminal showing the shared tests passing on the JVM and the iOS simulator"
   caption="Shared tests passing on both targets. Click to open full size."
   link=true width="1600" height="700" %}
```
{% endraw %}

`width` and `height` are the file's real pixel size. They let the browser reserve space before the image loads, so the text doesn't jump.
</details>

### Wide figure

`class="wide"` lets a large screenshot extend beyond the text column on desktop, up to 960 px. On phones it fits the screen like any other image.

{% include figure.html src="/assets/demo/everything-a-post-can-do/test-run.png" alt="The same terminal screenshot, shown wider than the text" caption='The same screenshot with `class="wide"`.' class="wide" width="1600" height="700" %}

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
{% include figure.html src="/assets/images/posts/slug/test-run.png"
   alt="…" caption="…" class="wide" width="1600" height="700" %}
```
{% endraw %}
</details>

### Phone screenshot

A full-width phone screenshot would be taller than the screen. `class="phone"` keeps it at 280 px wide, with rounded corners and a thin frame.

{% include figure.html src="/assets/demo/everything-a-post-can-do/android-items.webp" alt="Android app showing a list of seven items in Material 3 cards" caption="The Android app (a rendered mockup)." class="phone" width="600" height="1334" %}

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
{% include figure.html src="/assets/images/posts/slug/android-items.webp"
   alt="Android app showing a list of seven items in Material 3 cards"
   caption="The Android app." class="phone" width="600" height="1334" %}
```
{% endraw %}
</details>

### Side by side

Wrap figures in `<div class="gallery">` to put them next to each other. This works well for comparing Android and iOS. The figures sit side by side on phones too, as long as each can be at least 140 px wide.

<div class="gallery">
{% include figure.html src="/assets/demo/everything-a-post-can-do/android-items.webp" alt="Android version of the items list" caption="Android" class="phone" width="600" height="1334" %}
{% include figure.html src="/assets/demo/everything-a-post-can-do/ios-items.webp" alt="iOS version of the items list with a large title and grouped rows" caption="iOS" class="phone" width="600" height="1299" %}
</div>

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
<div class="gallery">
{% include figure.html src="/assets/images/posts/slug/android-items.webp"
   alt="Android version of the items list" caption="Android" class="phone" %}
{% include figure.html src="/assets/images/posts/slug/ios-items.webp"
   alt="iOS version of the items list" caption="iOS" class="phone" %}
</div>
```
{% endraw %}

Keep each include on a line with no blank lines between them. A blank line inside the `<div>` ends the HTML block.
</details>

### Screen recording

Give the `figure` include an `.mp4` instead of an image and it plays like a GIF: automatically, muted and on a loop. An MP4 is far smaller than the same clip as a GIF. This 5-second clip is 58 KB.

{% include figure.html src="/assets/demo/everything-a-post-can-do/loading.mp4" webm="/assets/demo/everything-a-post-can-do/loading.webm" poster="/assets/demo/everything-a-post-can-do/android-items.webp" alt="Recording: a loading spinner, then list items appearing one by one" caption="Items loading on Android." class="phone" width="600" height="1334" %}

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
{% include figure.html src="/assets/images/posts/slug/loading.mp4"
   webm="/assets/images/posts/slug/loading.webm"
   poster="/assets/images/posts/slug/android-items.webp"
   alt="Recording: a loading spinner, then list items appearing one by one"
   caption="Items loading on Android." class="phone" %}
```
{% endraw %}

`poster` is the frame shown before the video starts. Use the last frame, so readers with slow connections still see the result.

`webm` is optional. MP4 (H.264) plays in Chrome, Safari and Firefox, but some Chromium-based apps can't decode it. Adding a WebM copy covers those too; browsers use the first one they support:

```console
$ ffmpeg -i demo-small.mp4 -c:v libvpx-vp9 -crf 36 -b:v 0 -an demo-small.webm
```
</details>

### Cover image and link previews

The image at the top of this post comes from front matter, not the body. The same image becomes the preview card when the post is shared on LinkedIn, Slack or X. Use 1,200 × 630 px.

<details markdown="1"><summary>Markdown</summary>

```yaml
---
title: "Everything a post can do"
image: /assets/images/posts/slug/cover.jpg
image_alt: "Title card reading Everything a post can do"
---
```

Without `image`, the post has no cover and shares as a text-only link.
</details>

### Capturing and compressing

Take screenshots straight from the emulator and simulator, so there's no desktop clutter to crop:

```console
$ adb exec-out screencap -p > screen.png
$ adb shell screenrecord /sdcard/demo.mp4   # Ctrl+C to stop
$ adb pull /sdcard/demo.mp4
$ xcrun simctl io booted screenshot screen.png
$ xcrun simctl io booted recordVideo demo.mp4
```

Then shrink them before committing. `cwebp` and `ffmpeg` come from `brew install webp ffmpeg`. `sips` is built into macOS.

```console
$ cwebp -q 82 -resize 600 0 screen.png -o screen.webp
$ ffmpeg -i demo.mp4 -vf "scale=600:-2" -c:v libx264 -crf 26 -an -movflags +faststart demo-small.mp4
$ sips -Z 1600 wide-screenshot.png
```

Aim for these sizes:

| What | Format | Export width | Typical size |
|:--|:--|--:|--:|
| Phone screenshot | WebP or PNG | 600 px | 20–60 KB |
| Desktop screenshot | PNG or WebP | 1,600 px | 50–200 KB |
| Diagram | SVG | about 440 px | 1–10 KB |
| Photo | JPEG or WebP | 1,600 px | 100–300 KB |
| Screen recording | MP4 (H.264) | 600 px | 50–500 KB |
| Cover image | JPEG | 1,200 × 630 px | 50–150 KB |

## Video embeds

The `youtube` include embeds a talk at the full column width in 16:9. It uses YouTube's privacy-enhanced domain and only loads when scrolled into view.

{% include youtube.html id="F5NaqGF9oT4" title="KotlinConf'25 keynote" caption="KotlinConf'25 keynote, from the Kotlin by JetBrains channel." %}

<details markdown="1"><summary>Markdown</summary>

{% raw %}
```liquid
{% include youtube.html id="F5NaqGF9oT4" title="KotlinConf'25 keynote"
   caption="KotlinConf'25 keynote, from the Kotlin by JetBrains channel." %}
```
{% endraw %}

The `id` is the part after `v=` in the video's URL.
</details>

## Text

Paragraphs can use **bold**, *italic*, ~~strikethrough~~ and `inline code`. Keyboard shortcuts look like keys: <kbd>Shift</kbd> <kbd>Shift</kbd> opens Search Everywhere, and <kbd>⌘</kbd> <kbd>⇧</kbd> <kbd>A</kbd> opens Find Action. You can <mark>highlight a phrase</mark>, write O(n<sup>2</sup>), and hover over KMP or AGP to see what they stand for.

Links can go to [another site](https://kotlinlang.org/docs/multiplatform.html) or to a [section of this post](#callouts). Footnotes collect at the bottom of the page.[^mockups]

<details markdown="1"><summary>Markdown</summary>

```markdown
**bold**, *italic*, ~~strikethrough~~, `inline code`
<kbd>Shift</kbd> <kbd>Shift</kbd>
<mark>highlight a phrase</mark>, O(n<sup>2</sup>)
[another site](https://kotlinlang.org/docs/multiplatform.html)
[section of this post](#callouts)
Footnotes collect at the bottom.[^mockups]

[^mockups]: The footnote text, anywhere in the post.
*[KMP]: Kotlin Multiplatform
*[AGP]: Android Gradle Plugin
```

Every heading gets an anchor made from its text in lowercase with hyphens, e.g. `#video-embeds`. Abbreviation lines (`*[KMP]: …`) can go anywhere in the post and apply to every use of the word.
</details>

## Lists

- Bullet lists for things in no particular order
- They can nest:
  - `commonMain` for shared code
  - `androidMain` and `iosMain` for platform code

1. Numbered lists for steps
2. Where the order matters
3. Like a release checklist

- [x] Task lists for checklists
- [x] Checked items render ticked
- [ ] Unchecked items stay empty

Engine
: The part of Ktor that sends HTTP requests on a platform.

Source set
: A group of Kotlin files compiled for one or more targets.

<details markdown="1"><summary>Markdown</summary>

```markdown
- Bullet
  - Nested bullet (indent two spaces)

1. Numbered step

- [x] Checked task
- [ ] Unchecked task

Engine
: Definition, on the line after the term.
```
</details>

## Callouts

> **Note:** Background or context the reader may want.
{: .note}

> **Tip:** A shortcut or better way to do something.
{: .tip}

> **Warning:** Something that breaks, loses data or costs time.
{: .warning}

A blockquote without a class is a plain quote:

> Make it work, make it right, make it fast.
>
> — Kent Beck

<details markdown="1"><summary>Markdown</summary>

```markdown
> **Tip:** A shortcut or better way to do something.
{: .tip}
```

The class line goes directly under the quote: `.note`, `.tip` or `.warning`. Use one or two callouts per post at most.
</details>

## Code

A fenced block with a language gets syntax highlighting:

```kotlin
// shared/src/commonMain/kotlin/lt/setkus/api/ItemsApi.kt
class ItemsApi(private val client: HttpClient) {
    suspend fun items(): List<Item> = client.get("items").body()
}
```

The `console` language colors the prompt so commands stand out from their output:

```console
$ ./gradlew :shared:iosSimulatorArm64Test
> Task :shared:iosSimulatorArm64Test
BUILD SUCCESSFUL in 41s
```

`diff` shows a change:

```diff
-    implementation(libs.retrofit)
+    implementation(project(":shared"))
```

Line numbers help when the text refers to a specific line. Here, line 3 is the one that matters:

{% highlight kotlin linenos %}
fun createHttpClient(engine: HttpClientEngine): HttpClient =
    HttpClient(engine) {
        expectSuccess = true
    }
{% endhighlight %}

Long output can go in a collapsed block, so it doesn't interrupt the reading:

<details markdown="1"><summary>Full test report</summary>

```console
$ ./gradlew :shared:allTests --console=plain
> Task :shared:compileKotlinIosSimulatorArm64
> Task :shared:linkDebugTestIosSimulatorArm64
> Task :shared:iosSimulatorArm64Test
> Task :shared:testDebugUnitTest
> Task :shared:allTests
BUILD SUCCESSFUL in 1m 12s
```
</details>

<details markdown="1"><summary>Markdown</summary>

~~~markdown
```kotlin
// path/to/File.kt
```

{% raw %}{% highlight kotlin linenos %}
…
{% endhighlight %}{% endraw %}

<details markdown="1"><summary>Full test report</summary>

```console
…
```
</details>
~~~

Jekyll reads `{{ "{{" }}` and `{{ "{%" }}` as template tags, even inside code blocks. For code that contains them, such as GitHub Actions `${{ "{{" }} secrets.TOKEN }}`, put `{% raw %}{% raw %}{% endraw %}` on the line before the block and `{{ "{%" }} endraw %}` on the line after.
</details>

## Tables

| Engine | Platform | Artifact |
|:--|:--|:--|
| OkHttp | Android | `ktor-client-okhttp` |
| Darwin | iOS | `ktor-client-darwin` |
| MockEngine | Tests | `ktor-client-mock` |

<details markdown="1"><summary>Markdown</summary>

```markdown
| Engine | Platform | Artifact |
|:--|:--|--:|
| OkHttp | Android | `ktor-client-okhttp` |
```

The colons set alignment: `:--` left, `:-:` center, `--:` right. Keep tables to three or four columns so they fit on phones.
</details>

## Page structure

- `##` starts a section and `###` a subsection. The title is the page's only `#` heading.
- `* TOC` followed by `{:toc}` on the next line builds the contents box at the top from the headings. It's worth adding once a post has five or more sections.
- `---` on its own line draws a divider, like this:

---

- Front matter at the top of the file sets everything outside the body:

```yaml
---
title: "Sentence-case title"        # required
description: "One sentence."        # index, feed, link previews
tags: [kmp, kotlin]                 # 1–3 from the guide's list
image: /assets/images/posts/slug/cover.jpg
image_alt: "What the cover shows"   # needed with image
updated: 2026-10-02                 # optional, shows "Updated"
---
```

[^mockups]: The phone screenshots and the recording in this post are rendered mockups, made for the demo. They aren't a real app.

*[KMP]: Kotlin Multiplatform
*[AGP]: Android Gradle Plugin
