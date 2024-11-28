"""Module contain main page."""
from datetime import datetime
from typing import TYPE_CHECKING

from flet import BorderRadius
from flet import Column
from flet import Container
from flet import ControlEvent
from flet import Dropdown
from flet import ListTile
from flet import Margin
from flet import Padding
from flet import Text
from flet import TextStyle
from flet import colors
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
        years, months = self.core.filters_data(str(today.year))

        self.presentator = WorkPresentator(main)

        self.dropdown_year = Dropdown(
            label="Год",
            value=str(today.year),
            on_change=self.change_dropdowns,
            padding=Padding(left=10, top=5, right=10, bottom=0),
        )

        self.dropdown_month = Dropdown(
            label="Месяц",
            value=str(today.month) if today.month >= 10 else f"0{today.month}",
            on_change=self.change_dropdowns,
            padding=Padding(left=10, top=5, right=10, bottom=0),
        )

        self._load_filters(years, months)

        self.work_column = Column(controls=self.get_works())

        self.bottom_container = Container(
            Column([]),
            border_radius=BorderRadius(
                top_left=12,
                top_right=12,
                bottom_left=0,
                bottom_right=0,
            ),
            bgcolor=colors.SURFACE_VARIANT,
        )

        super().__init__(
            controls=[
                Container(
                    content=Column([
                        self.dropdown_year,
                        self.dropdown_month,
                    ]),
                    bgcolor=colors.SURFACE_VARIANT,
                    border_radius=BorderRadius(
                        top_left=0,
                        top_right=0,
                        bottom_left=15,
                        bottom_right=15,
                    ),
                    margin=Margin(left=0, top=0, right=0, bottom=20),
                    padding=Padding(left=0, top=10, right=0, bottom=10),
                ),
                self.work_column,
                self.bottom_container,
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
        bottom_container = Container(
            Column([
                ListTile(
                    trailing=Text(f"Итог: {str(month_money_value)} руб."),
                    leading_and_trailing_text_style=TextStyle(size=20),
                ),
                Container(height=52),
            ]),
            border_radius=BorderRadius(
                top_left=12,
                top_right=12,
                bottom_left=0,
                bottom_right=0,
            ),
            # bgcolor=colors.SURFACE_VARIANT,
        )
        works.append(bottom_container)
        return works

    def _load_filters(self, years: map, months: dict[str, str]) -> None:
        self.dropdown_year.options = [
            dropdown.Option(
                content=Text(year),
                key=year,
            )
            for year in years
        ]

        month_key = self.dropdown_month.value
        if month_key not in months:
            keys = tuple(months.keys())
            month_key = keys[-1] if keys else None

        self.dropdown_month.options = [
            dropdown.Option(
                content=Text(month_name),
                key=key,
            )
            for key, month_name in months.items()
        ]
        self.dropdown_month.value = month_key

    def change_dropdowns(self, event: ControlEvent | CreateWorkDayView):
        """Reload works after change dropdowns."""
        control = getattr(event, "control", event)
        if isinstance(control, CreateWorkDayView) or control.label == "Год":
            years, months = self.core.filters_data(self.dropdown_year.value)
            self._load_filters(years, months)

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
