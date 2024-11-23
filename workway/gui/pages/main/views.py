"""Module contain main page."""
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

from flet import AppBar
from flet import Chip
from flet import Column
from flet import ControlEvent
from flet import DatePicker
from flet import Divider
from flet import Dropdown
from flet import ElevatedButton
from flet import ResponsiveRow
from flet import ScrollMode
from flet import Text
from flet import TextField
from flet import TimePicker
from flet import View
from flet import dropdown


if TYPE_CHECKING:
    from datetime import time

    from workway.core.db.tables import BonusRow
    from workway.core.db.tables import RateRow
    from workway.core.subcores import WorkMaker


class CreateWorkDayView(View):
    """View for creating new work day."""

    def __init__(self, main) -> None:
        """Initialize."""
        self.core: WorkMaker = main
        today = datetime.now()

        self.rates: dict[str, RateRow] = self.core.get_rates()
        self.bonuses: list[BonusRow] = self.core.get_bonuses()

        # result values
        self.start_dt: datetime = today
        self.start_tm: time = self.start_dt.time()

        self.end_dt: datetime = today
        self.end_tm: time = self.start_dt.time()

        self.rate: RateRow | None = None
        if self.rates:
            self.rate = next(self.rates.values().__iter__())
        self.selected_bonuses = [
            bonus
            for bonus in self.bonuses
            if bonus.by_default
        ]

        # Controls

        # text field
        self.name_field = TextField(
            value="",
            label="Наименование",
            autofocus=True,
        )

        # labels
        self.start_dt_label = Text(
            self.start_dt.strftime(r"%d.%m.%y"),
            col={"md": 2},
        )
        self.start_tm_label = Text(
            self.start_dt.strftime(r"%H:%M"),
            col={"md": 2},
        )

        self.end_dt_label = Text(
            self.start_dt.strftime(r"%d.%m.%y"),
            col={"md": 2},
        )
        self.end_tm_label = Text(
            self.start_dt.strftime(r"%H:%M"),
            col={"md": 2},
        )
        self.bonus_label = Text("Надбавки")

        # pickers
        self.start_dt_picker = DatePicker(
            current_date=self.start_dt,
            value=self.start_dt,
            first_date=datetime(year=today.year - 1, month=2, day=1),
            last_date=datetime(year=today.year + 1, month=2, day=1),
            on_change=self.select_start_date,
        )
        self.start_tm_picker = TimePicker(
            value=today.time(),
            on_change=self.select_start_tm,
        )

        self.end_dt_picker = DatePicker(
            current_date=self.end_dt,
            value=self.end_dt,
            first_date=datetime(year=today.year - 1, month=1, day=1),
            last_date=datetime(year=today.year + 1, month=2, day=1),
            on_change=self.select_end_date,
        )
        self.end_tm_picker = TimePicker(
            value=today.time(),
            on_change=self.select_end_tm,
        )

        # dropdown
        self.rate_dropdown = Dropdown(
            label="Ставка",
            options=[
                dropdown.Option(
                    content=Text(
                        f"{rate.name} - {rate.value}"
                    ),
                    key=key,
                )
                for key, rate in self.rates.items()
            ],
            value=str(self.rate.id) if self.rate else None,
            on_change=self.select_rate,
        )

        # Chip
        self.bonus_chips = ResponsiveRow(
            [
                Chip(
                    label=Text(f"{bonus.name} +{bonus.value}"),
                    on_select=self.select_bonus,
                    selected=True,
                    col={"md": 3},
                ) if bonus.by_default else
                Chip(
                    label=Text(f"{bonus.name} +{bonus.value}"),
                    on_select=self.select_bonus,
                    col={"md": 3},
                )
                for bonus in self.bonuses
            ],
        )
        if not self.bonuses:
            self.bonus_chips.visible = False
            self.bonus_label.visible = False

        # buttons
        self.end_dt_tm_by_rate_button = ElevatedButton(
            "Задать по часам ставки",
            on_click=self.select_end_tm_by_rate,
            col={"md": 3},
        )

        super().__init__(
            appbar=AppBar(
                title=Text("Создание нового выхода на работу"),
            ),
            scroll=ScrollMode.ALWAYS,
            controls=[
                self.name_field,
                Divider(),
                Column(
                    controls=[
                        self.rate_dropdown,
                        self.bonus_label,
                        self.bonus_chips,
                        Divider(),
                        Text("Начало рабочего дня"),
                        ResponsiveRow(
                            controls=[
                                self.start_dt_label,
                                self.start_tm_label,
                            ]
                        ),
                        ResponsiveRow(
                            controls=[
                                ElevatedButton(
                                    "Задать дату",
                                    on_click=lambda e: self.page.open(
                                        self.start_dt_picker,
                                    ),
                                    col={"md": 2},
                                ),
                                ElevatedButton(
                                    "Задать время",
                                    on_click=lambda e: self.page.open(
                                        self.start_tm_picker,
                                    ),
                                    col={"md": 2},
                                )
                            ]
                        ),
                        Text("Конец рабочего дня"),
                        ResponsiveRow(
                            controls=[
                                self.end_dt_label,
                                self.end_tm_label,
                            ],
                        ),
                        ResponsiveRow(
                            controls=[
                                ElevatedButton(
                                    "Задать дату",
                                    on_click=lambda e: self.page.open(
                                        self.end_dt_picker,
                                    ),
                                    col={"md": 3},
                                ),
                                ElevatedButton(
                                    "Задать время",
                                    on_click=lambda e: self.page.open(
                                        self.end_tm_picker,
                                    ),
                                    col={"md": 3},
                                ),
                                self.end_dt_tm_by_rate_button,
                            ]
                        ),
                        Divider(),
                    ],
                ),
                ElevatedButton(
                    "Сохранить",
                    on_click=self.save_work,
                ),
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
        self.end_dt = self.end_dt_picker.value
        self.end_dt_label.value = self.end_dt.strftime(  # type: ignore
            r"%d.%m.%y",
        )
        self.update()

    def select_end_tm(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.end_tm = self.end_tm_picker.value
        self.end_tm_label.value = self.end_tm.strftime(  # type: ignore
            r"%H:%M",
        )
        self.update()

    def select_rate(self, event: ControlEvent) -> None:
        """Select rate"""
        control: Dropdown = event.control
        self.rate = self.rates[control.value]  # type: ignore
        if self.rate.type == "hour":
            self.end_dt_tm_by_rate_button.visible = False
            self.update()
            return
        self.end_dt_tm_by_rate_button.visible = True
        self.update()

    def select_end_tm_by_rate(self, event: ControlEvent) -> None:
        """Change end tm by hourn in rate."""
        start_tm = self.start_tm_picker.value
        start_dt = self.start_dt_picker.value
        if start_tm is None or start_dt is None or self.rate is None:
            return
        start_datetime = datetime(
            year=start_dt.year,
            month=start_dt.month,
            day=start_dt.day,
            hour=start_tm.hour,
            minute=start_tm.minute,
        )
        end_datetime = start_datetime + timedelta(hours=self.rate.hours)
        self.end_dt_picker.value = end_datetime
        self.end_tm_picker.value = end_datetime.time()
        self.select_end_date(event)
        self.select_end_tm(event)

    def select_bonus(self, event: ControlEvent) -> None:
        """Select bonus."""
        control: Chip = event.control
        bonus_index = self.bonus_chips.controls.index(control)
        selected_bonus = self.bonuses[bonus_index]
        match control.selected:
            case True:
                self.selected_bonuses.append(selected_bonus)
            case False:
                self.selected_bonuses.remove(selected_bonus)

    @property
    def is_valid(self) -> bool:
        """Validate controls data."""
        error_flag = True

        if self.rate is None:
            error_flag = False
            self.rate_dropdown.error_text = "Нужно выбрать ставку"

        return error_flag

    def save_work(self, event: ControlEvent) -> None:
        """Validate controls value and save work day."""
        if self.is_valid is False:
            self.update()
            return
        self.core.save_work(
            self.rate,  # type: ignore
            self.selected_bonuses,
            self.start_dt,
            self.start_tm,
            self.end_dt,
            self.end_tm,
            name=self.name_field.value,
        )
        self.page.views.pop()
        self.page.update()

