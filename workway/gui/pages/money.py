"""Module contain rate and bonus page."""
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any

from flet import AlertDialog
from flet import Checkbox
from flet import Column
from flet import ControlEvent
from flet import ElevatedButton
from flet import KeyboardType
from flet import ListTile
from flet import PopupMenuButton
from flet import PopupMenuItem
from flet import Text
from flet import TextField
from flet import icons


if TYPE_CHECKING:
    from workway.core.pages import Money


__all__ = (
    "MoneyPage",
)


class Rate(ListTile):
    """Rate gui element."""

    def __init__(self, rate) -> None:
        self.rate = rate
        super().__init__(
            leading=Text("💰"),
            title=Text(self.rate.name),
            subtitle=Text(self.rate.value),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(text="Изменить"),
                    PopupMenuItem(text="Удалить"),
                ],
            ),
        )


class RateModal(AlertDialog):

    def __init__(self, money) -> None:
        """Initialize."""
        self.money: Money = money

        self.name = TextField(
            label="Наименование",
            autofocus=True,
        )
        self.value = TextField(
            label="Сумма",
            keyboard_type=KeyboardType.NUMBER,
        )
        self.hours = TextField(
            label="Длительность смены в часах",
            keyboard_type=KeyboardType.NUMBER,
        )
        self.type = Checkbox(
            label="Почасовая ставка",
            on_change=self.on_change_type,
        )
        self.by_default = Checkbox(label="По умолчанию")

        super().__init__(
            modal=True,
            title=Text("Создание ставки"),
            content=Column(
                [
                    self.name,
                    self.value,
                    self.type,
                    self.hours,
                    self.by_default,
                ],
            ),
            actions=[
                ElevatedButton("Закрыть", on_click=self.close_modal),
                ElevatedButton("Созранить", on_click=self.save_modal),
            ],
        )

    def close_modal(self, event: ControlEvent) -> None:
        """Close this modal."""
        self.page.close(self)  # type: ignore

    @property
    def is_valid(self) -> bool:
        """Validate data."""
        error_flag = True

        if not self.value.value:
            self.value.error_text = "Обязательное поле"
            error_flag = False

        if not self.type.value and not self.hours.value:
            self.hours.error_text = "Обязательное поле"
            error_flag = False
        return error_flag

    def save_modal(self, event: ControlEvent) -> None:
        """Save this modal."""
        self.value.error_text = None
        self.hours.error_text = None

        if self.is_valid is False:
            self.update()
            return

        self.money.add_rate(
            {
                "name": self.name.value,
                "value": self.value.value,
                "by_default": self.by_default.value,
                "hours": self.hours.value,
                "type": self.type.value,
            }
        )
        self.page.close(self)  # type: ignore

    def on_change_type(self, event: ControlEvent) -> None:
        if event.data == "true":
            self.hours.visible = False
            self.update()
            return
        self.hours.visible = True
        self.update()


class MoneyPage(Column):
    """Money page contain controls for CRUD rate and bonus."""

    def __init__(self, money) -> None:
        """Initialize."""
        self.money: Money = money
        super().__init__(
            controls=self.get_controls(),
        )

    def get_controls(self) -> list:
        """Create controls."""
        return [
            Text("Ставка"),
            self.rates,
            Text("Надбавки"),
            self.bonuses,
        ]

    def add_rate(self, event: ControlEvent) -> None:
        """Create new rate obj."""
        self.rates.controls.insert(-1, Text("test"))
        self.rates.update()

    @cached_property
    def rates(self) -> Column:
        rates = [Rate(rate) for rate in self.money.all_rate()]  # noqa: F841
        add_button = ElevatedButton(
            "Добавить ставку",
            on_click=lambda e: self.page.open(  # type: ignore
                RateModal(self.money)
            ),
        )
        return Column(
            controls=[
                add_button,
                *rates,
            ],
        )

    def add_bonus(self, event: ControlEvent) -> None:
        """Create new rate obj."""
        self.bonuses.controls.insert(-1, Text("test"))
        self.bonuses.update()

    @cached_property
    def bonuses(self) -> Column:
        bonuses = self.money.all_bonus
        return Column(
            controls=[
                ElevatedButton("Добавить надбавку", on_click=self.add_bonus)
            ],
        )
