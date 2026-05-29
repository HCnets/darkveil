from .engine import ThemeEngine, ThemeBase
from .modern import ModernTheme
from .xp_luna import XPLunaBlue, XPLunaSilver, XPLunaOlive
from .win2k import Win2000Theme
from .win98 import Win98Theme
from .cyberpunk import CyberpunkTheme
from .dracula import DraculaTheme
from .nord import NordTheme
from .aero import AeroTheme
from .frutiger import FrutigerAeroTheme

ALL_THEMES = [
    ModernTheme,
    AeroTheme,
    FrutigerAeroTheme,
    XPLunaBlue,
    XPLunaSilver,
    XPLunaOlive,
    Win2000Theme,
    Win98Theme,
    CyberpunkTheme,
    DraculaTheme,
    NordTheme,
]

__all__ = [
    "ThemeEngine", "ThemeBase", "ALL_THEMES",
    "ModernTheme", "AeroTheme", "FrutigerAeroTheme",
    "XPLunaBlue", "XPLunaSilver", "XPLunaOlive",
    "Win2000Theme", "Win98Theme",
    "CyberpunkTheme", "DraculaTheme", "NordTheme",
]
