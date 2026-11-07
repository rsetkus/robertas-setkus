"""Build fixtures and HTML helpers for the setkus.lt test suite.

Every build runs in its own temporary copy of the site, so tests never touch
the real `_site/`, `.jekyll-cache/` or `_posts/`, and parallel runs don't
collide. See _docs/testing.md.
"""

import os
import shutil
import subprocess
import warnings
from pathlib import Path

import pytest
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_POSTS = Path(__file__).resolve().parent / "fixtures" / "posts"

# Top-level entries never copied into a temporary build.
SKIP_TOP_LEVEL = {
    ".git", ".claude", ".sage", ".jekyll-cache", ".pytest_cache",
    "_site", "_output", "_tests",
}


class BuildError(RuntimeError):
    """Jekyll exited nonzero. The message holds its stderr."""


def _jekyll():
    path = shutil.which("jekyll")
    if path is None:
        pytest.exit(
            "jekyll is not on PATH. Install it (gem install jekyll) and retry.",
            returncode=2,
        )
    return path


def build(tmp, posts=(), dev=False):
    """Build a copy of the site in `tmp` and return the output folder.

    posts: paths of Markdown files to place in the copy's `_posts/`.
    dev:   also load `_config.dev.yml` (drafts, unpublished posts, demo assets).
           Without it, the build runs with JEKYLL_ENV=production, like GitHub Pages.
    """
    tmp = Path(tmp)
    src = tmp / "src"
    dest = tmp / "site"
    shutil.copytree(
        REPO_ROOT,
        src,
        ignore=lambda d, names: SKIP_TOP_LEVEL & set(names)
        if Path(d) == REPO_ROOT else set(),
    )
    if posts:
        (src / "_posts").mkdir(exist_ok=True)
        for post in posts:
            shutil.copy(post, src / "_posts" / Path(post).name)

    cmd = [_jekyll(), "build", "--disable-disk-cache",
           "--source", str(src), "--destination", str(dest)]
    if dev:
        cmd += ["--config", f"{src / '_config.yml'},{src / '_config.dev.yml'}"]
    env = dict(os.environ, JEKYLL_NO_BUNDLER_REQUIRE="true")
    env["JEKYLL_ENV"] = "development" if dev else "production"

    result = subprocess.run(cmd, cwd=src, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise BuildError(f"jekyll build failed:\n{result.stderr or result.stdout}")
    return dest


def html(site, path):
    """Parse a built page. `path` is relative to the site root, e.g. "blog/index.html"."""
    file = Path(site) / path
    assert file.is_file(), f"{path} was not built"
    return BeautifulSoup(file.read_text(encoding="utf-8"), "html.parser")


def xml(site, path):
    """Parse a built XML file such as feed.xml (with the stdlib parser, no lxml)."""
    file = Path(site) / path
    assert file.is_file(), f"{path} was not built"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
        return BeautifulSoup(file.read_text(encoding="utf-8"), "html.parser")


def exists(site, path):
    """True if `path` (file or folder, relative to the site root) was built."""
    return (Path(site) / path).exists()


@pytest.fixture(scope="session")
def prod_site(tmp_path_factory):
    """The real site as GitHub Pages would build it, with no fixture posts."""
    return build(tmp_path_factory.mktemp("prod"))


@pytest.fixture(scope="session")
def fixture_site(tmp_path_factory):
    """A production build with every post in _tests/fixtures/posts/."""
    return build(tmp_path_factory.mktemp("fixture"),
                 posts=sorted(FIXTURE_POSTS.glob("*.md")))


@pytest.fixture(scope="session")
def dev_site(tmp_path_factory):
    """A local-preview build with _config.dev.yml (drafts and demo content shown)."""
    return build(tmp_path_factory.mktemp("dev"), dev=True)
