"""Module contain app."""
# from flet import app
from flet import Page
from .gui.base import MainComponent
from .core.component import Core


def main(page: Page) -> None:
    """Create base app."""
    core = Core("local.db")
    page.views.clear()
    page.views.append(MainComponent(core))
    page.update()



# app(main)
