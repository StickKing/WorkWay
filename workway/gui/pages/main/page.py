"""Module contain main page."""
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

from flet import AppBar
from flet import Chip
from flet import Column
from flet import ControlEvent
from flet import DatePicker
from flet import Dropdown
from flet import ElevatedButton
from flet import ResponsiveRow
from flet import ScrollMode
from flet import Text
from flet import TextField
from flet import TimePicker
from flet import View
from flet import dropdown

from .views import CreateWorkDayView


if TYPE_CHECKING:
    from datetime import time

    from workway.core.db.tables import BonusRow
    from workway.core.db.tables import RateRow
    from workway.core.subcores import Main
    from workway.core.subcores import WorkMaker
    from workway.gui.base import MainComponent


class MainPage(Column):

    def __init__(self, main):
        self.core: Main = main
        today = datetime.now()
        years, months = self.core.filters_data()
        self.core.get_works(today.year, today.month)

        self.dropdown_year = Dropdown(
            label="Год",
            value=str(today.year),
            options=[
                dropdown.Option(
                    content=Text(year),
                    key=year,
                )
                for year in years
            ]
        )

        self.dropdown_month = Dropdown(
            label="Месяц",
            value=str(today.month),
            options=[
                dropdown.Option(
                    content=Text(month_name),
                    key=key,
                )
                for key, month_name in months.items()
            ]
        )
        super().__init__(
            controls=[
                self.dropdown_year,
                self.dropdown_month,
            ]
        )

    @property
    def main_view(self) -> "MainComponent":
        """Return main view."""
        return self.page.views[0]

    def floating_action(self, event: ControlEvent) -> None:
        """Open creting work day view."""
        self.page.views.append(CreateWorkDayView(self.core.work_maker))
        self.page.update()
