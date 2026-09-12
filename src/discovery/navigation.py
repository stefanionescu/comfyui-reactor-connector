"""Extract model guide identities from Reactor's rendered documentation navigation."""

import re
from .contracts import invalid
from html.parser import HTMLParser
from ..state.discovery import Guide
from ...config.discovery import MAX_MODEL_GUIDES, GUIDE_PATH_PATTERN_TEXT


GUIDE_PATH = re.compile(GUIDE_PATH_PATTERN_TEXT)


class GuideLinks(HTMLParser):
    """Read anchors as data; never execute scripts or follow discovered addresses."""

    def __init__(self) -> None:
        """Decode HTML character references and start an empty set of model guide names."""
        super().__init__(convert_charrefs=True)
        self.slugs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect only valid model guide anchors within the catalog size limit."""
        if tag != "a":
            return
        hrefs = [value for key, value in attrs if key == "href"]
        if len(hrefs) != 1 or hrefs[0] is None:
            return
        match = GUIDE_PATH.fullmatch(hrefs[0])
        if match:
            self.slugs.add(match.group(1))
            if len(self.slugs) > MAX_MODEL_GUIDES:
                raise invalid()


def navigation_guides(text: str) -> tuple[Guide, ...]:
    """Return distinct model guide names from the public navigation document."""
    parser = GuideLinks()
    parser.feed(text)
    parser.close()
    if not parser.slugs:
        raise invalid()
    # Navigation anchors say "Overview". Retain the stable slug until a source
    # supplies a model title; guessing a title can obscure a new model's identity.
    return tuple(Guide(slug, slug) for slug in sorted(parser.slugs))
