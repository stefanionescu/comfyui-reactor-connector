"""Collect model examples and their live-control variations."""

from .live import live_examples
from .models.helios import SEQUENCE_EXAMPLES
from .models.x2 import EXAMPLES as X2_EXAMPLES
from .models.ltx import EXAMPLES as LTX_EXAMPLES
from .models.fast import EXAMPLES as FAST_EXAMPLES
from .models.sana import EXAMPLES as SANA_EXAMPLES
from .models.visko import EXAMPLES as VISKO_EXAMPLES
from .models.helios import EXAMPLES as HELIOS_EXAMPLES
from .models.lingbot import EXAMPLES as LINGBOT_EXAMPLES
from .models.longlive import EXAMPLES as LONGLIVE_EXAMPLES

BASE_EXAMPLES = (
    *FAST_EXAMPLES,
    *HELIOS_EXAMPLES,
    *LINGBOT_EXAMPLES,
    *LONGLIVE_EXAMPLES,
    *LTX_EXAMPLES,
    *SANA_EXAMPLES,
    *VISKO_EXAMPLES,
    *X2_EXAMPLES,
)

EXAMPLES = (*BASE_EXAMPLES, *live_examples(BASE_EXAMPLES), *SEQUENCE_EXAMPLES)
