"""Module contain app."""
# from flet import app
from flet import ControlEvent
from flet import Page
from flet import app

from .core import Core
from .gui.base import MainComponent


def main(page: Page) -> None:
    """Create base app."""
    core = Core()
    page.views.clear()
    page.views.append(MainComponent(core))
    page.update()

    def view_pop(event: ControlEvent) -> None:
        """Back to previous view."""
        page.views.pop()
        page.update()

    page.on_view_pop = view_pop


app(main)
