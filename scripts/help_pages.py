"""Build local, readable help pages and resolve links inside ComfyUI."""

import html
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from quality.repository import visible_files

PREFIX = "/extensions/reactor-inc/guides/"
STYLE = """
:root { color-scheme: light dark; font: 16px/1.6 system-ui, sans-serif; }
body { margin: 0 auto; max-width: 76ch; padding: 2rem 1.25rem 4rem; }
a { color: light-dark(#174b99, #9fc6ff); text-underline-offset: .15em; }
h1, h2, h3 { line-height: 1.25; margin-top: 1.5em; }
table { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
th, td { text-align: left; vertical-align: top; padding: .6rem; border: 1px solid GrayText; }
pre { overflow-x: auto; padding: 1rem; background: light-dark(#f1f3f5, #20242a); }
code { overflow-wrap: anywhere; } li { margin-block: .4rem; }
nav { display: flex; flex-wrap: wrap; gap: 1rem; }
"""


class HelpPages:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.public_files = set(visible_files(self.root))
        self.files: dict[Path, bytes] = {}
        self.visited: set[Path] = set()
        self.parser = MarkdownIt("js-default")

    def link(self, source: Path, target: str) -> str:
        parts = urlsplit(target)
        if parts.scheme or not parts.path or parts.path.startswith("/"):
            return target
        path = (source.parent / unquote(parts.path)).resolve()
        if path.is_dir():
            path /= "README.md"
        relative = path.relative_to(self.root)
        if (
            not path.is_file()
            or path not in self.public_files
            or relative.name == "PLAN.md"
            or relative.parts[0].startswith(".")
        ):
            raise ValueError(f"Repair the help link in {source.name}.")
        if path.suffix == ".md":
            self.page(path)
            name = relative.with_suffix(".html")
        else:
            name = Path("files") / relative
            self.files[self.root / "web/guides" / name] = path.read_bytes()
        return PREFIX + name.as_posix() + ("#" + parts.fragment if parts.fragment else "")

    def markdown(self, source: Path) -> bytes:
        """Resolve native Info links against the installed extension, not the canvas URL."""
        self.require_public_source(source)
        text = re.sub(
            r"\]\(([^)]+)\)",
            lambda match: "](" + self.link(source, match[1]) + ")",
            source.read_text(),
        )
        return text.encode()

    def require_public_source(self, source: Path) -> None:
        if (
            source not in self.public_files
            or source.resolve() not in self.public_files
            or source.is_symlink()
            or not source.is_file()
        ):
            raise ValueError("Help pages must come from public repository files.")

    def page(self, source: Path) -> None:
        self.require_public_source(source)
        if source in self.visited:
            return
        self.visited.add(source)
        text = source.read_text()
        tokens = self.parser.parse(text)
        for index, token in enumerate(tokens):
            if token.type == "heading_open" and index + 1 < len(tokens):
                title = tokens[index + 1].content
                token.attrSet("id", re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-"))
            for child in token.children or []:
                if child.type == "link_open":
                    target = child.attrGet("href")
                    if isinstance(target, str) and target:
                        child.attrSet("href", self.link(source, target))
        title = html.escape(text.splitlines()[0].lstrip("# "))
        body = self.parser.renderer.render(tokens, self.parser.options, {})
        page = (
            f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{title}</title><style>{STYLE}</style></head><body>"
            '<nav aria-label="Reactor guides">'
            f'<a href="{PREFIX}README.html">Reactor for ComfyUI</a>'
            f'<a href="{PREFIX}workflows/README.html">Workflows</a>'
            f'<a href="{PREFIX}docs/live.html">Live controls</a></nav>'
            f"<main>{body}</main></body></html>\n"
        )
        self.files[
            self.root / "web/guides" / source.relative_to(self.root).with_suffix(".html")
        ] = page.encode()

    def build(self) -> dict[Path, bytes]:
        for name in ("README.md", "workflows/README.md"):
            self.page(self.root / name)
        for source in sorted(self.public_files):
            if not source.is_relative_to(self.root / "docs") or source.suffix != ".md":
                continue
            self.page(source)
        return self.files
