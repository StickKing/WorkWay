"""Module contain base elements."""
from typing import TYPE_CHECKING

from flet import AppBar
from flet import ControlEvent
from flet import NavigationBar
from flet import NavigationBarDestination
from flet import SafeArea
from flet import Text
from flet import View
from flet import icons
from flet_core.control import Control

from .pages import MoneyPage


if TYPE_CHECKING:
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
                ],
                on_change=self.change_page,
            ),
            appbar=AppBar(visible=False),
        )

    def change_page(self, event: ControlEvent) -> None:
        """Navigation by main menu."""
        match event.control.selected_index:
            case 0:
                self.content = Text("view control 1")
            case 1:
                self.content = MoneyPage(self.core.money)

    @property
    def content(self) -> Control:
        """Fetch current control."""
        return self.controls[0]

    @content.setter
    def content(self, control: Control) -> None:
        """Set new control."""
        self.controls.clear()
        self.controls.append(SafeArea(control))
        self.update()
