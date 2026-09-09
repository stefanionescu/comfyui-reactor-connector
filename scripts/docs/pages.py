"""Build local, readable help pages and resolve links inside ComfyUI."""

import re
import html
import json
import posixpath
from pathlib import Path
from string import Template
from markdown_it import MarkdownIt
from markdown_it.token import Token
from ...config.routes import HELP_PREFIX
from urllib.parse import unquote, urlsplit
from ...config.models.nodes import NODE_MODELS
from ...config.security import LANGUAGE_PATTERN
from ...quality.lib.files import git_visible_files
from ...src.language import translate, language_scope


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
        self.languages = dict.fromkeys(self.sources, "en")
        for node_id in NODE_MODELS:
            for source in (self.root / "web/docs" / node_id).glob("*.md"):
                if not re.fullmatch(LANGUAGE_PATTERN, source.stem):
                    message = "Node guide language filenames must use a supported locale tag."
                    raise ValueError(message)
                self.sources[source] = Path("nodes") / node_id / source.with_suffix(".html").name
                self.languages[source] = source.stem
        template = self.root / "web/help/template.html"
        self.require_public_source(template)
        self.template = Template(template.read_text().replace("<!doctype html>", "<!DOCTYPE html>").replace(" />", ">"))
        self.output = self.root / "web/dist/guides"

    def link(self, source: Path, target: str, *, native: bool = False) -> str:
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
        url = HELP_PREFIX + name.as_posix() if native else self.relative_url(source, name)
        return url + ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")

    def markdown(self, source: Path) -> bytes:
        """Resolve native Info links against the installed extension, not the canvas URL."""
        self.require_public_source(source)
        text = re.sub(
            r"\]\(([^)]+)\)",
            lambda match: "](" + self.link(source, match[1], native=True) + ")",
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
        title = text.splitlines()[0].lstrip("# ")
        body = self.parser.renderer.render(tokens, self.parser.options, {})
        language = self.languages[source]
        with language_scope(language):
            slots = {
                "language": language,
                "direction": "rtl" if language.split("-", 1)[0] in {"ar", "fa", "he", "ur"} else "ltr",
                "title": title,
                "stylesheet": self.relative_url(source, Path("docs.css")),
                "navigation": translate("main", "help.navigation"),
                "project_url": self.relative_url(source, Path("README.html")),
                "project_label": translate("main", "help.project"),
                "workflows_url": self.relative_url(source, Path("workflows/README.html")),
                "workflows_label": translate("main", "help.workflows"),
                "controls_url": self.relative_url(source, Path("ADVANCED.html")) + "#live-controls",
                "controls_label": translate("main", "help.liveControls"),
            }
        page = self.template.substitute({key: html.escape(value) for key, value in slots.items()}, body=body)
        page = page.replace('dir="ltr"', f'dir="{slots["direction"]}"', 1)
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
                    if attribute == "href" and not urlsplit(resolved).scheme and "files/" in resolved:
                        child.attrSet("download", Path(urlsplit(resolved).path).name)

    def relative_url(self, source: Path, target: Path) -> str:
        """Resolve an asset from the generated page, independent of its installation folder."""
        return posixpath.relpath(target.as_posix(), self.sources[source].parent.as_posix())

    def build(self) -> dict[Path, bytes]:
        """Render every canonical guide and return the complete output file mapping."""
        for source in self.sources:
            self.page(source)
        self.files[self.output / "docs.css"] = (self.root / "web/styles/docs.css").read_bytes()
        languages = {
            node_id: [self.languages[source] for source in self.sources if node_id in {source.stem, source.parent.name}]
            for node_id in NODE_MODELS
        }
        self.files[self.output / "languages.json"] = (json.dumps(languages, indent=2) + "\n").encode()
        return self.files
