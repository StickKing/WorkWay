"""Module contain app."""

from flet import ControlEvent
from flet import Page
from flet import ThemeMode
from flet import app

from .core import Core
from .gui.base import MainComponent


def prepare_theme(page: Page, core: "Core") -> None:
    """Prepare theme."""
    match core.settings.current_theme:
        case "dark":
            page.theme_mode = ThemeMode.DARK
        case "light":
            page.theme_mode = ThemeMode.LIGHT


def main(page: Page) -> None:
    """Create base app."""
    core = Core()
    prepare_theme(page, core)
    page.views.clear()
    page.views.append(MainComponent(core))
    page.update()

    def view_pop(event: ControlEvent) -> None:
        """Back to previous view."""
        page.views.pop()
        page.update()

    page.on_view_pop = view_pop


app(main, assets_dir="assets")
