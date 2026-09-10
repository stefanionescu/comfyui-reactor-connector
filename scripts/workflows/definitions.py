"""Collect model examples and their live-control variations."""

from .models.helios import SEQUENCE_EXAMPLES
from .models.x2 import EXAMPLES as X2_EXAMPLES
from .models.ltx import EXAMPLES as LTX_EXAMPLES
from .models.fast import EXAMPLES as FAST_EXAMPLES
from .models.sana import EXAMPLES as SANA_EXAMPLES
from .models.visko import EXAMPLES as VISKO_EXAMPLES
from .models.helios import EXAMPLES as HELIOS_EXAMPLES
from .models.lingbot import EXAMPLES as LINGBOT_EXAMPLES
from .models.x2 import LIVE_EXAMPLES as X2_LIVE_EXAMPLES
from .models.longlive import EXAMPLES as LONGLIVE_EXAMPLES
from .models.sana import LIVE_EXAMPLES as SANA_LIVE_EXAMPLES
from .models.visko import LIVE_EXAMPLES as VISKO_LIVE_EXAMPLES
from .models.helios import LIVE_EXAMPLES as HELIOS_LIVE_EXAMPLES
from .models.longlive import LIVE_EXAMPLES as LONGLIVE_LIVE_EXAMPLES

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

EXAMPLES = (
    *BASE_EXAMPLES,
    *HELIOS_LIVE_EXAMPLES,
    *LONGLIVE_LIVE_EXAMPLES,
    *SANA_LIVE_EXAMPLES,
    *VISKO_LIVE_EXAMPLES,
    *X2_LIVE_EXAMPLES,
    *SEQUENCE_EXAMPLES,
)
