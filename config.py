"""Loads API keys from environment variables or a local .env file.

Keys are never stored in the source code. See .env.example.
"""
import os
from pathlib import Path


def _load_env_file(path=Path(__file__).with_name(".env")):
    """Read KEY=value lines from .env into os.environ (without overriding existing values)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


def _require(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(
            f"Missing {name}. Copy .env.example to .env and add your own key "
            f"(see README.md)."
        )
    return value


OPENWEATHER_KEY = _require("OPENWEATHER_API_KEY")
WAQI_KEY = _require("WAQI_API_TOKEN")
