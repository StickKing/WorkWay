"""Module contain main page."""
from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Callable

from flet import AppBar
from flet import BorderRadius
from flet import ButtonStyle
from flet import Chip
from flet import Column
from flet import Container
from flet import ControlEvent
from flet import DatePicker
from flet import Divider
from flet import Dropdown
from flet import ElevatedButton
from flet import IconButton
from flet import KeyboardType
from flet import Margin
from flet import Padding
from flet import ResponsiveRow
from flet import Row
from flet import ScrollMode
from flet import SnackBar
from flet import Switch
from flet import Text
from flet import TextField
from flet import TextStyle
from flet import TextThemeStyle
from flet import TimePicker
from flet import View
from flet import colors
from flet import dropdown
from flet import icons


if TYPE_CHECKING:
    from datetime import time

    from workway.core.db.tables import BonusRow
    from workway.core.db.tables import RateRow
    from workway.core.subcores import WorkMaker
    from workway.typings import TCompleteBonus
    from workway.typings import TCompleteOtherIncome
    from workway.typings import TCompleteRework


class BonusChip(Row):

    controls: tuple[Chip, Switch]

    def __init__(
        self,
        bonus: "BonusRow",
        on_select: Callable,
    ) -> None:
        """Initialize."""
        self.bonus = bonus
        super().__init__((
            Chip(
                label=Text(
                    f"{bonus.name} +{bonus.value}"
                    if bonus.type == "fix"
                    else f"{bonus.name} {bonus.value}%"
                ),
                on_select=on_select,
                selected=True if bonus.by_default else False,
            ),
            Switch(
                "Учесть переработку",
                visible=False,
                disabled=True if bonus.type == "fix" else False,
                label_style=TextStyle(size=12),
            ),
        ))

    @property
    def selected(self) -> bool:
        """Check chip selected."""
        return self.controls[0].selected

    @property
    def completed_bonus(self) -> TCompleteBonus:
        """Return completed bonus."""
        return {
            "bonus": self.bonus,
            "on_full_sum": self.controls[1].value,
        }

    @property
    def swith(self) -> Switch:
        """Swith visiability property."""
        return self.controls[1]


class OtherIncome(Row):
    """Row for adding other income money."""

    def __init__(self) -> None:
        """Initialize."""
        self.name_field = TextField(
            label="Наименование",
            autofocus=True,
            width=150,
        )
        self.money_field = TextField(
            label="Сумма",
            width=150,
        )
        super().__init__([
            self.name_field,
            self.money_field,
            IconButton(
                icon=icons.HIGHLIGHT_REMOVE,
                on_click=self.delete_this,
            ),
        ])

    def delete_this(self, event: ControlEvent) -> None:
        """Delete with row from parent control."""
        self.parent.controls.remove(self)
        self.parent.update()


class CreateWorkDayView(View):
    """View for creating new work day."""

    def __init__(self, main) -> None:
        """Initialize."""
        self.core: WorkMaker = main
        today = datetime.now()
        self.rework_flag = False

        self.rates: dict[str, RateRow] = self.core.get_rates()

        # result values
        self.start_dt: datetime = today
        self.start_tm: time = self.start_dt.time()

        self.end_dt: datetime = today
        self.end_tm: time = self.start_dt.time()

        self.rate: RateRow | None = None
        if self.rates:
            self.rate = next(self.rates.values().__iter__())

        self.other_income = []

        # Controls

        # rework controls
        self.rework_lable = Text(
            "Обнаружена переработка",
            theme_style=TextThemeStyle.TITLE_MEDIUM,
        )
        self.rework_checkbox = Switch(
            "Не учитывать",
            value=False,
        )
        self.rework_percent = TextField(
            label="% ставки / час",
            keyboard_type=KeyboardType.NUMBER,
        )
        self.rework_fix_sum = TextField(
            label="Фиксированная сумма",
            keyboard_type=KeyboardType.NUMBER,
        )
        self.rework_column = Container(
            content=Column([
                self.rework_lable,
                self.rework_checkbox,
                self.rework_percent,
                self.rework_fix_sum,
            ]),
            visible=False,
            bgcolor=colors.ON_ERROR,
            border_radius=12,
            padding=Padding(
                left=10,
                top=15,
                right=10,
                bottom=15,
            ),
        )

        # text field
        self.name_field = TextField(
            value="",
            label="Наименование",
            autofocus=True,
        )

        # labels
        self.start_dt_label = ElevatedButton(
            self.start_dt.strftime(r"%d.%m.%y"),
            col={"md": 2},
            on_click=lambda e: self.page.open(
                self.start_dt_picker,
            ),
        )

        self.start_tm_label = ElevatedButton(
            self.start_dt.strftime(r"%H:%M"),
            col={"md": 2},
            on_click=lambda e: self.page.open(
                self.start_tm_picker,
            ),
        )

        self.end_dt_label = ElevatedButton(
            self.start_dt.strftime(r"%d.%m.%y"),
            col={"md": 2},
            on_click=lambda e: self.page.open(
                self.end_dt_picker,
            ),
        )

        self.end_tm_label = ElevatedButton(
            self.start_dt.strftime(r"%H:%M"),
            col={"md": 2},
            on_click=lambda e: self.page.open(
                self.end_tm_picker,
            ),
        )
        self.bonus_label = Text(
            "Надбавки",
            theme_style=TextThemeStyle.TITLE_MEDIUM,
        )

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
            options=[
                dropdown.Option(
                    content=Text(
                        f"{rate.name} +{rate.value} руб."
                    ),
                    key=key,
                )
                for key, rate in self.rates.items()
            ],
            value=str(self.rate.id) if self.rate else None,
            on_change=self.select_rate,
        )

        bonus_chip_list = []
        self.selected_bonuses_indexes = []
        for index, bonus in enumerate(self.core.get_bonuses()):
            bonus_chip_list.append(BonusChip(bonus, self.select_bonus))
            if bonus.by_default:
                self.selected_bonuses_indexes.append(index)

        self.bonus_chips = Column(bonus_chip_list)

        if not bonus_chip_list:
            self.bonus_chips.visible = False
            self.bonus_label.visible = False

        # buttons
        self.end_dt_tm_by_rate_button = ElevatedButton(
            "По часам ставки",
            on_click=self.select_end_tm_by_rate,
            col={"md": 3},
        )

        # work datetime control

        start_container = Container(
            content=Column([
                Container(
                    Text(
                        "Начало рабочего дня",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    margin=Margin(left=0, top=0, right=0, bottom=5),
                ),
                Row(
                    controls=[
                        self.start_dt_label,
                        self.start_tm_label,
                    ],
                ),
            ]),
        )

        end_container = Container(
            content=Column([
                Container(
                    Text(
                        "Конец рабочего дня",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    margin=Margin(left=0, top=0, right=0, bottom=5),
                ),
                Row(
                    controls=[
                        self.end_dt_label,
                        self.end_tm_label,
                    ],
                ),
                self.end_dt_tm_by_rate_button,
            ])
        )

        self.other_income_column = Column([
            Text(
                "Доп. доход",
                theme_style=TextThemeStyle.TITLE_MEDIUM,
            ),
            IconButton(
                icon=icons.ADD,
                style=ButtonStyle(bgcolor=colors.BLACK),
                on_click=self.add_other_income,
                width=50,
                height=50,
            ),
        ])

        super().__init__(
            appbar=AppBar(
                title=Text("Создание нового выхода на работу"),
                bgcolor=colors.SURFACE_VARIANT,
            ),
            scroll=ScrollMode.HIDDEN,
            padding=0,
            controls=[
                Container(
                    self.name_field,
                    border_radius=BorderRadius(
                        top_left=0,
                        top_right=0,
                        bottom_left=12,
                        bottom_right=12,
                    ),
                    bgcolor=colors.SURFACE_VARIANT,
                    padding=Padding(
                        left=10,
                        top=15,
                        right=10,
                        bottom=15,
                    ),
                ),
                Container(
                    Column([
                        Text(
                            "Ставка",
                            theme_style=TextThemeStyle.TITLE_MEDIUM,
                        ),
                        self.rate_dropdown,
                        self.bonus_label,
                        self.bonus_chips,
                        Container(
                            self.other_income_column,
                            margin=Margin(left=0, top=0, right=0, bottom=10),
                        )
                    ]),
                    margin=Margin(left=0, top=2, right=0, bottom=2),
                    padding=Padding(
                        left=10,
                        top=15,
                        right=10,
                        bottom=15,
                    ),
                    border_radius=12,
                    bgcolor=colors.SURFACE_VARIANT,
                ),
                Container(
                    Column([
                        start_container,
                        Divider(),
                        end_container,
                    ]),
                    margin=Margin(left=0, top=0, right=0, bottom=2),
                    padding=Padding(
                        left=10,
                        top=15,
                        right=0,
                        bottom=5,
                    ),
                    border_radius=12,
                    bgcolor=colors.SURFACE_VARIANT,
                ),
                self.rework_column,
                Container(
                    ResponsiveRow(
                        controls=[
                            ElevatedButton(
                                "Сохранить",
                                on_click=self.save_work,
                                height=50,
                            ),
                        ],
                    ),
                    margin=Margin(left=0, top=0, right=0, bottom=2),
                ),
            ]
        )

    def select_start_date(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.start_dt = event.control.value
        self.start_dt_label.text = self.start_dt.strftime(r"%d.%m.%y")
        self.update()

    def select_start_tm(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.start_tm = self.start_tm_picker.value
        self.start_tm_label.text = self.start_tm.strftime(r"%H:%M")
        self.update()

    def select_end_date(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.end_dt = self.end_dt_picker.value
        self.end_dt_label.text = self.end_dt.strftime(  # type: ignore
            r"%d.%m.%y",
        )
        self.update()

    def select_end_tm(self, event: ControlEvent) -> None:
        """After seleted date change gui."""
        self.end_tm = self.end_tm_picker.value
        self.end_tm_label.text = self.end_tm.strftime(  # type: ignore
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
        control: BonusChip = event.control.parent
        bonus: BonusRow = control.bonus
        bonus_chip_index = self.bonus_chips.controls.index(control)
        match control.selected, bonus.type:
            case True, "fix":
                self.selected_bonuses_indexes.append(bonus_chip_index)
            case True, "percent":
                control.swith.visible = True
                self.selected_bonuses_indexes.append(bonus_chip_index)
            case False, "fix":
                self.selected_bonuses_indexes.remove(bonus_chip_index)
            case False, "percent":
                control.swith.visible = False
                control.swith.value = False
                self.selected_bonuses_indexes.remove(bonus_chip_index)
        self.update()

    def add_other_income(self, event: ControlEvent) -> None:
        self.other_income_column.controls.insert(
            -1,
            OtherIncome(),
        )
        self.other_income_column.update()

    @property
    def is_valid(self) -> bool:
        """Validate controls data."""
        error_flag = True

        if self.rate is None:
            error_flag = False
            self.rate_dropdown.error_text = "Нужно выбрать ставку"

        if self.completed_start_dttm > self.completed_end_dttm:
            error_flag = False
            self.page.snack_bar = SnackBar(
                Text("Дата начала не может быть меньше даты конца")
            )
            self.page.snack_bar.open = True
            self.page.update()

        difference = self.completed_end_dttm - self.completed_start_dttm
        work_hours = difference.total_seconds() // 60 // 60

        if self.rework_flag is False and work_hours > self.rate.hours:
            error_flag = False
            self.rework_lable.value = "Обнаружена переработка {} {}".format(
                int(work_hours - self.rate.hours),
                "часов",
            )
            self.rework_column.visible = True
            self.rework_flag = True
            return error_flag

        if self.rework_flag:
            self.rework_fix_sum.error_text = ""
            self.rework_percent.error_text = ""

            if (
                self.rework_checkbox.value is False and
                not self.rework_fix_sum.value and
                not self.rework_percent.value
            ):
                msg = "Нужно выбрать один из вариантов"
                self.rework_fix_sum.error_text = msg
                self.rework_percent.error_text = msg
                error_flag = False
                return error_flag

            if (
                self.rework_percent.value and
                self.rework_percent.value.isdigit() is False
            ):
                msg = "Процент должен быть целым числом"
                self.rework_percent.error_text = msg
                error_flag = False
                return error_flag

            if (
                self.rework_fix_sum.value and
                self.rework_fix_sum.value.isalpha() is True
            ):
                self.rework_fix_sum.error_text = "Сумма должена быть числом"
                error_flag = False

        return error_flag

    @property
    def completed_rework(self) -> TCompleteRework | None:
        """Create rework if it exists."""
        if not self.rework_flag or self.rework_checkbox.value:
            return None
        percent = self.rework_percent.value
        if percent:
            return {
                "type": "%",
                "value": int(percent),
            }
        fix_sum = self.rework_fix_sum.value
        if fix_sum:
            return {
                "type": "sum",
                "value": float(fix_sum),
            }
        return None

    @property
    def completed_bonuses(self) -> list[TCompleteBonus]:
        bonus_chips = self.bonus_chips.controls
        return [
            bonus_chips[bonus_index].completed_bonus
            for bonus_index in self.selected_bonuses_indexes
        ]

    @cached_property
    def completed_start_dttm(self) -> datetime:
        """Completely result start datetime."""
        return datetime(
            year=self.start_dt.year,
            month=self.start_dt.month,
            day=self.start_dt.day,
            hour=self.start_tm.hour,
            minute=self.start_tm.minute,
        )

    @cached_property
    def completed_end_dttm(self) -> datetime:
        """Completely result start datetime."""
        return datetime(
            year=self.end_dt.year,
            month=self.end_dt.month,
            day=self.end_dt.day,
            hour=self.end_tm.hour,
            minute=self.end_tm.minute,
        )

    @property
    def completed_other_income(self) -> list[TCompleteOtherIncome]:
        """Return completed other income money."""
        controls: list[OtherIncome] = self.other_income_column.controls[1:-1]

        return [
            {
                "name": str(cont.name_field.value or cont.money_field.value),
                "value": value,
            }
            for cont in controls
            if (value := float(cont.money_field.value or 0)) > 0
        ]

    def save_work(self, event: ControlEvent) -> None:
        """Validate controls value and save work day."""
        if self.is_valid is False:
            self.update()
            del self.completed_start_dttm
            del self.completed_end_dttm
            return

        self.core.save_work(
            self.rate,  # type: ignore
            self.completed_bonuses,
            self.completed_start_dttm,
            self.completed_end_dttm,
            name=self.name_field.value,
            rework=self.completed_rework,
            other_income=self.completed_other_income,
        )
        self.page.views.pop()
        self.page.views[-1].content.change_dropdowns(self)
        self.page.update()