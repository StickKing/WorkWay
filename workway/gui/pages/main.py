"""Module contain main page."""
from datetime import datetime
from typing import TYPE_CHECKING

from flet import AppBar
from flet import Column
from flet import ControlEvent
from flet import DatePicker
from flet import Dropdown
from flet import ElevatedButton
from flet import Row
from flet import Text
from flet import TimePicker
from flet import View
from flet import dropdown


if TYPE_CHECKING:
    from workway.core.pages import Main
    from workway.gui.base import MainComponent


class CreateWorkDayView(View):
    """View for creating new work day."""

    def __init__(self, main) -> None:
        """Initialize."""
        self.main: Main = main
        today = datetime.now()

        self.rates: list = self.main.get_rates()
        self.rates.sort(key=lambda e: -e.by_default)

        # result values
        self.start_dt = today
        self.start_tm = self.start_dt.time()

        self.end_dt = today
        self.end_tm = self.start_dt.time()

        # labels
        self.start_dt_label = Text(self.start_dt.strftime(r"%d.%m.%y"))
        self.start_tm_label = Text(self.start_dt.strftime(r"%H:%M"))

        self.end_dt_label = Text(self.start_dt.strftime(r"%d.%m.%y"))
        self.end_tm_label = Text(self.start_dt.strftime(r"%H:%M"))

        # pickers
        start_dt_picker = DatePicker(
            current_date=self.start_dt,
            first_date=datetime(year=today.year - 1, month=2, day=1),
            last_date=datetime(year=today.year + 1, month=2, day=1),
            on_change=self.select_start_date,
        )

        end_dt_picker = DatePicker(
            first_date=datetime(year=today.year - 1, month=1, day=1),
            last_date=datetime(year=today.year + 1, month=2, day=1),
            on_change=self.select_end_date,
        )
        super().__init__(
            appbar=AppBar(),
            controls=[
                Text("Создание нового выхода на работу"),
                Column(
                    controls=[
                        Text("Ставка"),
                        Dropdown(
                            options=[
                                dropdown.Option(
                                    content=Text(f"{rate.name} - {rate.value}"),
                                    key=rate.id,
                                )
                                for rate in self.rates
                            ],
                            # value=self.rates[0],
                        ),
                        Text("Начало рабочего дня"),
                        Row(
                            controls=[
                                self.start_dt_label,
                                ElevatedButton(
                                    "Задать дату",
                                    on_click=lambda e: self.page.open(
                                        start_dt_picker,
                                    ),
                                ),
                            ]
                        ),
                        Row(
                            controls=[
                                self.start_tm_label,
                                ElevatedButton(
                                    "Задать время",
                                    on_click=lambda e: self.page.open(
                                        TimePicker(on_change=self.select_start_tm),
                                    ),
                                )
                            ]
                        ),
                        Text("Конец рабочего дня"),
                        Row(
                            controls=[
                                self.end_dt_label,
                                ElevatedButton(
                                    "Задать дату",
                                    on_click=lambda e: self.page.open(
                                        end_dt_picker,
                                    ),
                                ),
                            ]
                        ),
                        Row(
                            controls=[
                                self.end_tm_label,
                                ElevatedButton(
                                    "Задать время",
                                    on_click=lambda e: self.page.open(
                                        TimePicker(on_change=self.select_end_tm),
                                    ),
                                )
                            ]
                        )
                    ],
                )
            ]
        )

    def select_start_date(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.start_dt = event.control.value
        self.start_dt_label.value = self.start_dt.strftime(r"%d.%m.%y")
        self.update()

    def select_start_tm(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.start_tm = event.control.value
        self.start_tm_label.value = self.start_tm.strftime(r"%H:%M")
        self.update()

    def select_end_date(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.end_dt = event.control.value
        self.end_dt_label.value = self.end_dt.strftime(r"%d.%m.%y")
        self.update()

    def select_end_tm(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.end_tm = event.control.value
        self.end_tm_label.value = self.end_tm.strftime(r"%H:%M")
        self.update()


class MainPage(Column):

    def __init__(self, main):
        self.main: Main = main
        super().__init__(
            controls=[
                Text("Main page")
            ]
        )

    @property
    def main_view(self) -> "MainComponent":
        """Return main view."""
        return self.page.views[0]

    def floating_action(self, event: ControlEvent) -> None:
        """Open creting work day view."""
        self.page.views.append(CreateWorkDayView(self.main))
        self.page.update()
