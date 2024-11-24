"""Module contain main page."""
from datetime import datetime
from typing import TYPE_CHECKING

from flet import Column
from flet import ControlEvent
from flet import Dropdown
from flet import ListTile
from flet import Text
from flet import TextStyle
from flet import dropdown

from .presentator import WorkPresentator
from .presentator import WorkTile
from .views import CreateWorkDayView


if TYPE_CHECKING:
    from workway.core.subcores import Main
    from workway.gui.base import MainComponent


class MainPage(Column):

    def __init__(self, main):
        self.core: Main = main
        today = datetime.now()
        years, months = self.core.filters_data()

        self.presentator = WorkPresentator(main)

        self.dropdown_year = Dropdown(
            label="Год",
            value=str(today.year),
            on_change=self.change_dropdowns,
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
            value=str(today.month) if today.month >= 10 else f"0{today.month}",
            on_change=self.change_dropdowns,
            options=[
                dropdown.Option(
                    content=Text(month_name),
                    key=key,
                )
                for key, month_name in months.items()
            ],
        )

        self.work_column = Column(controls=self.get_works())
        
        super().__init__(
            controls=[
                self.dropdown_year,
                self.dropdown_month,
                self.work_column,
            ],
        )

    def get_works(self) -> list[WorkTile]:
        """Get works tile list."""
        works = []
        month_money_value = 0
        for work in self.core.get_works(
            self.dropdown_month.value,
            self.dropdown_year.value,
        ):
            works.append(WorkTile(work))
            month_money_value += work.value
        works.append(ListTile(
            trailing=Text(f"Итог: {str(month_money_value)} руб."),
            leading_and_trailing_text_style=TextStyle(size=20),
        ))
        return works

    def change_dropdowns(self, event: ControlEvent):
        """Reload works after change dropdowns."""
        self.work_column.controls = self.get_works()
        self.update()

    @property
    def main_view(self) -> "MainComponent":
        """Return main view."""
        return self.page.views[0]

    def floating_action(self, event: ControlEvent) -> None:
        """Open creting work day view."""
        self.page.views.append(CreateWorkDayView(self.core.work_maker))
        self.page.update()
