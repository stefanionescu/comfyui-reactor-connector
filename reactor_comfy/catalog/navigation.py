"""Extract model guide identities from Reactor's rendered documentation navigation."""

import re
from html.parser import HTMLParser

from .contracts import Guide, invalid

GUIDE_PATH = re.compile(
    r"(?:https://docs\.reactor\.inc)?/model-api-reference/"
    r"([a-z0-9][a-z0-9._-]{0,119})/overview(?:\.md)?/?"
)


class GuideLinks(HTMLParser):
    """Read anchors as data; never execute scripts or follow discovered addresses."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slugs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        hrefs = [value for key, value in attrs if key == "href"]
        if len(hrefs) != 1 or hrefs[0] is None:
            return
        match = GUIDE_PATH.fullmatch(hrefs[0])
        if match:
            self.slugs.add(match.group(1))
            if len(self.slugs) > 512:
                raise invalid()


def navigation_guides(text: str) -> tuple[Guide, ...]:
    parser = GuideLinks()
    parser.feed(text)
    parser.close()
    if not parser.slugs:
        raise invalid()
    # Navigation anchors say "Overview". Retain the stable slug until a source
    # supplies a model title; guessing a title can obscure a new model's identity.
    return tuple(Guide(slug, slug) for slug in sorted(parser.slugs))
