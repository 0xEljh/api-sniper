"""
API Sniper - A lightweight Python tool for reliably mimicking browser-initiated API calls
"""

from .config import SniperConfig
from .api_sniper import APISniper

__version__ = "0.1.0"
__author__ = "0xEljh"
__all__ = ["APISniper", "SniperConfig"]
