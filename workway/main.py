"""Module contain app."""
# from flet import app
from flet import Page

from .core import Core
from .gui.base import MainComponent


def main(page: Page) -> None:
    """Create base app."""
    core = Core()
    core.money.all()
    page.views.clear()
    page.views.append(MainComponent(core))
    page.update()



# app(main)
