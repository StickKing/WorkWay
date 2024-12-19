"""Module contain settings page subcore."""

from typing import TYPE_CHECKING
from typing import Literal

from .base import BaseCore


if TYPE_CHECKING:
    from pathlib import Path


Ttheme = Literal["dark", "light"]


class Settings(BaseCore):
    """Realize logic for setting page."""

    __slots__ = ("db", "core")

    @property
    def current_theme(self) -> None | Ttheme:
        """Return current theme."""
        theme = self.db.setting.get(key="theme")
        if theme is None:
            return "dark"
        match theme.value:
            case "dark":
                return "dark"
            case "light":
                return "light"

    @property
    def db_path(self) -> "Path":
        """Return db path."""
        return self.core.db_path

    @property
    def archive_path(self) -> "Path":
        """Return db path."""
        path: Path = self.core.db_path
        path = path / "work_way_archives"
        path.mkdir(exist_ok=True)
        return path

    def set_theme(self, theme_name: Ttheme):
        """Set theme in db."""
        theme = self.db.setting.get(key="theme")
        if theme is None:
            self.db.setting.add({
                "key": "theme",
                "value": theme_name,
            })
            theme = self.db.setting.get(key="theme")
        theme.value = theme_name
        theme.change()

    def reinitialize_db(self) -> None:
        """Reinitialize db obj."""
        self.core.reinitialize_db()
