"""Module contain base elements."""
from typing import TYPE_CHECKING

from flet import AppBar
from flet import ControlEvent
from flet import FloatingActionButton
from flet import NavigationBar
from flet import NavigationBarDestination
from flet import SafeArea
from flet import ScrollMode
from flet import View
from flet import icons

from .pages import MainPage
from .pages import MoneyPage
from .pages import SettingPage


if TYPE_CHECKING:
    from flet import Control

    from workway.core import Core


__all__ = (
    "MainComponent",
)


class MainComponent(View):
    """Main Component contains all gui elements."""

    def __init__(self, core) -> None:
        """Initialize main component."""
        self.core: Core = core
        super().__init__(
            padding=0,
            navigation_bar=NavigationBar(
                destinations=[
                    NavigationBarDestination(
                        icon=icons.HOME,
                        label="Главная",
                    ),
                    NavigationBarDestination(
                        icon=icons.ATTACH_MONEY,
                        label="Ставки и надбавки",
                    ),
                    NavigationBarDestination(
                        icon=icons.SETTINGS,
                        label="Настройки",
                    ),
                ],
                on_change=self.change_page,
            ),
            appbar=AppBar(visible=False),
            scroll=ScrollMode.HIDDEN,
            floating_action_button=FloatingActionButton(
                icon=icons.ADD,
                on_click=self.floating_action,
            ),
            controls=[
                SafeArea(MainPage(self.core.main)),
            ],
        )

    def floating_action(self, event: ControlEvent) -> None:
        self.content.floating_action(event)

    def change_page(self, event: ControlEvent) -> None:
        """Navigation by main menu."""
        match event.control.selected_index:
            case 0:
                self.floating_action_button.visible = True
                self.content = MainPage(self.core.main)
            case 1:
                self.floating_action_button.visible = False
                self.content = MoneyPage(self.core.money)
            case 2:
                self.floating_action_button.visible = False
                self.content = SettingPage(self.core.settings)

    @property
    def content(self) -> "Control":
        """Fetch current control."""
        return self.controls[0].content

    @content.setter
    def content(self, control: "Control") -> None:
        """Set new control."""
        self.controls.clear()
        self.controls.append(SafeArea(control))
        self.update()
