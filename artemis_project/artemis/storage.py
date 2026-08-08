"""
A tiny persisted State - same as State, but backed by a JSON file so the
value survives an app restart. Handy for "remember dark mode", "last
tab used", a small local todo list - anything you don't want to lose the
moment the window closes, without reaching for an actual database.

Values need to be JSON-serializable (numbers, strings, lists, dicts,
bools, None). Artemis deliberately doesn't try to pickle arbitrary Python
objects here - that gets fragile fast the moment your app's code changes.

Files land in a `.artemis_data/` folder next to your script, the same
way `assets/` does for branding - nothing hidden in some OS-specific
app-data folder you'd have to go hunting for.
"""

import json
import sys
from pathlib import Path

from .state import State

_DATA_DIRNAME = ".artemis_data"


def _data_dir():
    script_dir = Path(sys.argv[0]).resolve().parent if sys.argv and sys.argv[0] else Path.cwd()
    path = script_dir / _DATA_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _file_for(key):
    safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in key)
    return _data_dir() / f"{safe}.json"


class PersistentState(State):
    """
        theme_pref = art.PersistentState("theme", default="indigo")
        theme_pref.value = "forest"   # written to disk immediately, no extra step

    Reads whatever was saved last time on creation; falls back to
    `default` the first time it's ever used (and writes nothing to disk
    until you actually change it).
    """

    def __init__(self, key, default=None):
        self._path = _file_for(key)
        if self._path.exists():
            try:
                initial = json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                initial = default
        else:
            initial = default
        super().__init__(initial)

    @property
    def value(self):
        return State.value.fget(self)

    @value.setter
    def value(self, new_value):
        State.value.fset(self, new_value)
        try:
            self._path.write_text(json.dumps(new_value))
        except OSError:
            pass  # disk full, read-only fs, whatever - fail quietly rather than crash the app
