"""Module contain settings page subcore."""

from typing import Literal

from .base import BaseCore


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
