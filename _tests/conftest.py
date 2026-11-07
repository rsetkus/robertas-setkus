"""Build fixtures and HTML helpers for the setkus.lt test suite.

Every build runs in its own temporary copy of the site, so tests never touch
the real `_site/`, `.jekyll-cache/` or `_posts/`, and parallel runs don't
collide. See _docs/testing.md.
"""

import json
import os
import shutil
import subprocess
import warnings
from pathlib import Path

import pytest
import yaml
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


def _remove_keys(config_file, keys):
    """Delete dotted keys such as "analytics.counter_dev.id" from a YAML file.

    The file is rewritten without its comments; only the temporary copy is ever
    passed here. A key that isn't there raises KeyError, so a renamed setting
    fails loudly instead of making a test pass for the wrong reason.
    """
    data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    for key in keys:
        *parents, last = key.split(".")
        node = data
        for part in parents:
            node = node[part]
        del node[last]
    config_file.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8")


def build(tmp, posts=(), dev=False, config=None, env=None, remove=()):
    """Build a copy of the site in `tmp` and return the output folder.

    posts:  paths of Markdown files to place in the copy's `_posts/`.
    dev:    also load `_config.dev.yml` (drafts, unpublished posts, demo assets).
            Without it, the build runs with JEKYLL_ENV=production, like GitHub Pages.
    config: a dict loaded as one more `--config` file after the others. Jekyll
            deep-merges hashes, so it can change single values, for example
            {"analytics": {"counter_dev": {"id": "..."}}}. It can't remove a key.
    env:    the JEKYLL_ENV value. Default: "development" with dev=True,
            otherwise "production".
    remove: dotted keys deleted from the copy's `_config.yml` before the build,
            for example ["analytics"] or ["analytics.counter_dev.id"].
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
    if remove:
        _remove_keys(src / "_config.yml", remove)

    cmd = [_jekyll(), "build", "--disable-disk-cache",
           "--source", str(src), "--destination", str(dest)]
    configs = [src / "_config.yml"]
    if dev:
        configs.append(src / "_config.dev.yml")
    if config is not None:
        # JSON is valid YAML, so no YAML library is needed. The file sits
        # outside the source folder, so it is never copied into the site.
        override = tmp / "config.override.yml"
        override.write_text(json.dumps(config), encoding="utf-8")
        configs.append(override)
    if len(configs) > 1:
        cmd += ["--config", ",".join(str(c) for c in configs)]
    if env is None:
        env = "development" if dev else "production"
    jekyll_env = dict(os.environ, JEKYLL_NO_BUNDLER_REQUIRE="true", JEKYLL_ENV=env)

    result = subprocess.run(cmd, cwd=src, env=jekyll_env,
                            capture_output=True, text=True)
    # Kept next to the output folder (never inside it), for build_log().
    (tmp / "build.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise BuildError(f"jekyll build failed:\n{result.stderr or result.stdout}")
    return dest


def build_log(site):
    """Everything Jekyll printed (stdout, then stderr) while building `site`."""
    return (Path(site).parent / "build.log").read_text(encoding="utf-8")


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
