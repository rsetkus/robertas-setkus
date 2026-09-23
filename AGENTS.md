# Rules for agents

This is the Jekyll site for setkus.lt. GitHub Pages builds it from `main`, so anything merged into `main` goes live.

## Demo and debug content: never publish

Demo posts exist only to preview the blog's design. They live **only on the local `debug` branch**:

- `_drafts/everything-a-post-can-do.md`
- `_drafts/sharing-ktor-client-kmp.md`
- `assets/images/posts/everything-a-post-can-do/`
- `assets/images/posts/sharing-ktor-client-kmp/`

1. Never push the `debug` branch, to any remote, under any name.
2. Never merge, rebase, cherry-pick or copy `debug` commits or demo files into another branch.
3. Never move a demo post into `_posts/`, and never remove its `published: false`.
4. Never bypass the pre-push guard (`git push --no-verify`) or edit it to let demo content through.
5. Put new demo or debug content on `debug` only, and add its paths to this list and to `.githooks/pre-push`.

If a request would break one of these rules, stop and ask the user first, even if the request seems to require it.

To preview the demo posts: `git switch debug`, then `JEKYLL_NO_BUNDLER_REQUIRE=true jekyll serve --drafts --unpublished`.

## Pre-push guard

`.githooks/pre-push` refuses to push the `debug` branch, or any commit that contains the paths above. Install it once per clone (it covers every worktree):

```bash
cp .githooks/pre-push "$(git rev-parse --git-common-dir)/hooks/pre-push"
```

## Writing posts

Formats, templates and the writing guide are in `_templates/README.md`.
