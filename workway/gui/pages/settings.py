"""Module constain setting page."""
from __future__ import annotations

from typing import TYPE_CHECKING

from flet import BorderRadius
from flet import Column
from flet import Container
from flet import Margin
from flet import Padding
from flet import Radio
from flet import RadioGroup
from flet import Row
from flet import Switch
from flet import Text
from flet import TextThemeStyle
from flet import ThemeMode
from flet import colors


if TYPE_CHECKING:
    from flet import ControlEvent

    from workway.core.subcores import Settings


class SettingPage(Container):
    """Setting page."""

    def __init__(self, core: "Settings") -> None:
        """Initialize."""
        self.core = core

        self.theme_radio_group = RadioGroup(
            content=Row([
                Radio(value="light", label="Светлая"),
                Radio(value="dark", label="Тёмная"),
            ]),  # type: ignore
            on_change=self.change_app_theme,
            value=core.current_theme,
        )
        app_theme = Container(
            Column([
                    Text(
                        "Смена темы",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    self.theme_radio_group,
            ]),
            margin=Margin(0, 0, 0, 10),
            padding=Padding(left=15, top=10, right=0, bottom=10),
            bgcolor=colors.SURFACE_VARIANT,
            border_radius=BorderRadius(
                top_left=12,
                top_right=12,
                bottom_left=12,
                bottom_right=12,
            ),
        )
        super().__init__(
            content=Column([
                Container(
                    content=Text(
                        "Настройки",
                        theme_style=TextThemeStyle.TITLE_LARGE,
                    ),
                    margin=Margin(0, 0, 0, 30),
                ),
                app_theme,
            ]),
            padding=Padding(left=15, top=10, right=15, bottom=10),
        )

    def change_app_theme(self, event: "ControlEvent"):
        """Change app theme."""
        control: Switch = event.control
        match control.value:
            case "dark":
                self.page.theme_mode = ThemeMode.DARK
                self.core.set_theme("dark")
            case _:
                self.page.theme_mode = ThemeMode.LIGHT
                self.core.set_theme("light")
        self.page.update()
