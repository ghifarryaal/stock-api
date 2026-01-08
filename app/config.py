from __future__ import annotations
import os

APP_NAME = os.getenv("APP_NAME", "IDX Unified Market Intel API")
APP_VERSION = os.getenv("APP_VERSION", "3.0.0")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "2048"))

# Default behavior toggles
DEFAULT_WITH_FUNDAMENTAL = os.getenv("DEFAULT_WITH_FUNDAMENTAL", "true").lower() == "true"
DEFAULT_WITH_TECHNICAL = os.getenv("DEFAULT_WITH_TECHNICAL", "true").lower() == "true"
DEFAULT_WITH_WHALE = os.getenv("DEFAULT_WITH_WHALE", "true").lower() == "true"
DEFAULT_WITH_NEWS = os.getenv("DEFAULT_WITH_NEWS", "false").lower() == "true"
