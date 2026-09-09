"""Build local, readable help pages and resolve links inside ComfyUI."""

import re
import html
from pathlib import Path
from markdown_it import MarkdownIt
from markdown_it.token import Token
from ...src.language import translate
from urllib.parse import unquote, urlsplit
from ...config.models.nodes import NODE_MODELS
from ...quality.lib.files import git_visible_files

PREFIX = "/extensions/reactor-inc/guides/"


class HelpPages:
    """Render the authored user guides and copy only their public linked files."""

    def __init__(self, root: Path) -> None:
        """Select canonical guide sources and the public files they may reference."""
        self.root = root.resolve()
        self.public_files = {self.root / name for name in git_visible_files(root=self.root, is_existing_required=True)}
        self.files: dict[Path, bytes] = {}
        self.visited: set[Path] = set()
        self.parser = MarkdownIt("js-default")
        self.sources = {
            self.root / "README.md": Path("README.html"),
            self.root / "ADVANCED.md": Path("ADVANCED.html"),
            self.root / "workflows/README.md": Path("workflows/README.html"),
            **{self.root / "web/docs" / f"{node_id}.md": Path("nodes") / f"{node_id}.html" for node_id in NODE_MODELS},
        }
        self.output = self.root / "web/dist/guides"

    def link(self, source: Path, target: str) -> str:
        """Map a public guide or download link to its installed extension URL."""
        parts = urlsplit(target)
        if parts.scheme or not parts.path or parts.path.startswith("/"):
            return target
        candidate = source.parent / unquote(parts.path)
        if candidate.is_symlink() or any(parent.is_symlink() for parent in candidate.parents):
            msg = f"Remove the linked file from the guide in {source.name}."
            raise ValueError(msg)
        path = candidate.resolve()
        if path.is_dir():
            path /= "README.md"
        self.require_public_source(path)
        if path in self.sources:
            self.page(path)
            name = self.sources[path]
        else:
            relative = path.relative_to(self.root)
            if relative != Path("LICENSE.md") and not (
                relative.parts[0] == "workflows" and path.suffix in {".json", ".png", ".jpg", ".mp4"}
            ):
                msg = f"Link to a user guide or workflow file in {source.name}."
                raise ValueError(msg)
            name = Path("files") / relative
            self.files[self.output / name] = path.read_bytes()
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
        """Reject missing, ignored, symlinked, and out-of-repository guide inputs."""
        if (
            not source.is_relative_to(self.root)
            or source not in self.public_files
            or source.resolve() not in self.public_files
            or source.is_symlink()
            or not source.is_file()
        ):
            msg = "Help pages must come from public repository files."
            raise ValueError(msg)

    def page(self, source: Path) -> None:
        """Render one canonical guide with local links, heading anchors, and navigation."""
        self.require_public_source(source)
        if source not in self.sources:
            msg = "Only the named user guides can become help pages."
            raise ValueError(msg)
        if source in self.visited:
            return
        self.visited.add(source)
        text = source.read_text()
        tokens = self.parser.parse(text)
        for index, token in enumerate(tokens):
            if token.type == "heading_open" and index + 1 < len(tokens):
                title = tokens[index + 1].content
                token.attrSet("id", re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-"))
            self.rewrite_links(source, token)
        title = html.escape(text.splitlines()[0].lstrip("# "))
        body = self.parser.renderer.render(tokens, self.parser.options, {})
        page = (
            f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><link rel="stylesheet" href="{PREFIX}docs.css"></head><body>'
            f'<nav aria-label="{html.escape(translate("main", "help.navigation"))}">'
            f'<a href="{PREFIX}README.html">{html.escape(translate("main", "help.project"))}</a>'
            f'<a href="{PREFIX}workflows/README.html">{html.escape(translate("main", "help.workflows"))}</a>'
            f'<a href="{PREFIX}ADVANCED.html#live-controls">'
            f"{html.escape(translate('main', 'help.liveControls'))}</a></nav>"
            f"<main>{body}</main></body></html>\n"
        )
        self.files[self.output / self.sources[source]] = page.encode()

    def rewrite_links(self, source: Path, token: Token) -> None:
        """Resolve inline links and make bundled files download when selected."""
        for child in token.children or []:
            attribute = "href" if child.type == "link_open" else "src" if child.type == "image" else None
            if attribute:
                target = child.attrGet(attribute)
                if isinstance(target, str) and target:
                    resolved = self.link(source, target)
                    child.attrSet(attribute, resolved)
                    if attribute == "href" and resolved.startswith(PREFIX + "files/"):
                        child.attrSet("download", Path(urlsplit(resolved).path).name)

    def build(self) -> dict[Path, bytes]:
        """Render every canonical guide and return the complete output file mapping."""
        for source in self.sources:
            self.page(source)
        self.files[self.output / "docs.css"] = (self.root / "web/docs.css").read_bytes()
        return self.files
