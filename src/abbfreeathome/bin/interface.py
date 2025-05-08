"""
Defines the avaliable interfaces in the Free@Home System.

This is not a comprehensive list. To add new interfaces please open a GitHub issue:
https://github.com/kingsleyadam/local-abbfreeathome/issues
"""

import enum


class Interface(enum.Enum):
    """An Enum class for Free@Home interfaces."""

    UNDEFINED = None
    WIRED_BUS = "TP"
    WIRELESS_RF = "RF"
    HUE = "hue"
    SONOS = "sonos"
    VIRTUAL_DEVICE = "VD"
    SMOKEALARM = "smokealarm"
