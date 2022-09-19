"""Utilities for parsing document handles and series information.
"""

__all__ = ("SERIES", "DOCUMENT_HANDLE_PATTERN")

import re

SERIES = {
    "LPM": "LSST Project Management",
    "LSE": "LSST Systems Engineering",
    "LDM": "LSST Data Management",
    "DMTR": "LSST DM Test Report",
    "SQR": "SQuaRE Technical Note",
    "DMTN": "Data Management Technical Note",
    "SMTN": "Simulations Technical Note",
    "PSTN": "Project Science Team Technical Note",
    "SITCOMTN": "Systems Integration, Testing, and Commissioning Technical "
    "Note",
    "OPSTN": "LSST Operations Technical Note",
    "TSTN": "LSST Telescope & Site Technical Note",
}
"""Mapping between LSST document series (handle prefixes) and the title of the
series.
"""


DOCUMENT_HANDLE_PATTERN = re.compile(
    r"^(?P<series>" + "|".join([h for h in SERIES]) + ")" r"-(?P<serial>\d+)",
    re.IGNORECASE,
)
"""Pattern that matches the handle of any LSST document.

Notes
-----
The pattern exposes two named groups in the match object:

- ``'series'``. The document series. For example, ``'LDM'``.
- ``'serial'``. The serial number, as a `str`. For example, ``'151'``.

Note that the pattern is **case insensitive.** If you input text is normalized
to lower case, it will still match, but the series will be in lower case.

Examples
--------

>>> m = DOCUMENT_HANDLE_PATTERN.match('LDM-151'.lower())
>>> m.group('series')
'LDM'
>>> m.group('serial')
'151'
"""
