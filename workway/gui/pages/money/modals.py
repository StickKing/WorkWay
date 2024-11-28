"""Module contain rate and bonus page."""
from typing import TYPE_CHECKING

from flet import AlertDialog
from flet import Checkbox
from flet import Column
from flet import ControlEvent
from flet import Dropdown
from flet import ElevatedButton
from flet import KeyboardType
from flet import Text
from flet import TextField
from flet import dropdown

from workway.core.db.tables import BonusType
from workway.core.db.tables import RateType


if TYPE_CHECKING:
    from workway.core.subcores import Money


class RateModal(AlertDialog):
    """Rate modal for create new rate."""

    def __init__(self, money, on_dismiss=None) -> None:
        """Initialize."""
        self.money: Money = money
        # new created rate item
        self.new_rate: dict | None = None

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
        # self.type = Checkbox(
        #     label="Почасовая ставка",
        #     on_change=self.on_change_type,
        # )
        self.type = Dropdown(
            label="Тип",
            options=[
                dropdown.Option(
                    key=type_.name,
                    content=Text(type_.value)
                )
                for type_ in RateType
            ],
            value=RateType.shift.name,
            on_change=self.on_change_type,
        )
        self.by_default = Checkbox(label="По умолчанию")

        super().__init__(
            modal=True,
            title=Text("Создание ставки"),
            content=Column(
                [
                    self.name,
                    self.type,
                    self.value,
                    self.hours,
                    self.by_default,
                ],
            ),
            actions=[
                ElevatedButton("Закрыть", on_click=self.close_modal),
                ElevatedButton("Созранить", on_click=self.save_modal),
            ],
            on_dismiss=on_dismiss,
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

        if self.value.value.replace(".", "").isdigit() is False:
            self.value.error_text = "Должны быть только цифры"
            error_flag = False

        if not self.type.value and self.hours.value.isdigit is False:
            self.hours.error_text = "Должны быть только цифры"
            error_flag = False

        return error_flag

    def save_modal(self, event: ControlEvent) -> None:
        """Save this modal."""
        self.value.error_text = None
        self.hours.error_text = None

        if self.is_valid is False:
            self.update()
            return

        self.new_rate = self.money.add_rate(
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
        """Diasabled field by type."""
        match self.type.value:
            case "hour":
                self.hours.visible = False
            case "shift":
                self.hours.visible = True
        self.update()


class UpdateRateModal(RateModal):
    """Modal for updating rate."""

    def __init__(self, money, rate_item, on_dismiss=None) -> None:
        """Initialize."""
        super().__init__(money, on_dismiss)
        self.title = Text("Изменение ставки")
        self.rate_item = rate_item
        self.name.value = rate_item.name
        self.value.value = str(rate_item.value)
        self.by_default.value = bool(rate_item.by_default)
        self.hours.value = str(rate_item.hours)
        self.type.value = rate_item.type

    def save_modal(self, event: ControlEvent) -> None:
        """Save this modal."""
        self.value.error_text = None
        self.hours.error_text = None

        if self.is_valid is False:
            self.update()
            return

        new_rate = {
            "name": self.name.value,
            "value": self.value.value,
            "by_default": self.by_default.value,
            "hours": self.hours.value,
            "type": self.type.value,
        }

        # if value changed create new rate
        if float(self.rate_item.value) != float(new_rate["value"]):
            self.rate_item.state = 2
            self.rate_item.change()

            self.new_rate = self.money.add_rate(new_rate)
            self.page.close(self)
            return

        self.new_rate = self.money.update_item(new_rate, self.rate_item)
        self.page.close(self)  # type: ignore


class BonusModal(AlertDialog):
    """Rate modal for create new rate."""

    def __init__(self, money, on_dismiss=None) -> None:
        """Initialize."""
        self.money: Money = money
        # new created bonus item
        self.new_bonus: dict | None = None

        self.name = TextField(
            label="Наименование",
            autofocus=True,
        )
        self.value = TextField(
            label="Сумма",
            keyboard_type=KeyboardType.NUMBER,
        )
        self.type = Dropdown(
            label="Тип",
            options=[
                dropdown.Option(
                    key=type_.name,
                    content=Text(type_.value)
                )
                for type_ in BonusType
            ],
            value=BonusType.fix.name,
            on_change=self.change_type,
        )
        self.by_default = Checkbox(label="По умолчанию")

        super().__init__(
            modal=False,
            title=Text("Создание надбавки"),
            content=Column(
                [
                    self.name,
                    self.type,
                    self.value,
                    self.by_default,
                ],
            ),
            actions=[
                ElevatedButton("Закрыть", on_click=self.close_modal),
                ElevatedButton("Созранить", on_click=self.save_modal),
            ],
            on_dismiss=on_dismiss,
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

        if self.value.value.replace(".", "").isdigit() is False:
            self.value.error_text = "Должны быть только цифры"
            error_flag = False

            error_flag = False

        return error_flag

    def save_modal(self, event: ControlEvent) -> None:
        """Save this modal."""
        self.value.error_text = None

        if self.is_valid is False:
            self.update()
            return

        self.new_bonus = self.money.add_bonus(
            {
                "name": self.name.value,
                "value": self.value.value,
                "type": self.type.value,
                "by_default": self.by_default.value,
            }
        )
        self.page.close(self)  # type: ignore

    def change_type(self, event: ControlEvent):
        """Change label in value by type."""
        match self.type.value:
            case "fix":
                self.value.label = "Сумма"
            case "percent":
                self.value.label = "%"
        self.update()


class UpdateBonusModal(BonusModal):
    """Modal for updating rate."""

    def __init__(self, money, bonus_item, on_dismiss=None) -> None:
        """Initialize."""
        super().__init__(money, on_dismiss)
        self.title = Text("Изменение надбавки")
        self.bonus_item = bonus_item
        self.name.value = bonus_item.name
        self.type.value = bonus_item.type
        self.value.value = str(bonus_item.value)
        self.by_default.value = bool(bonus_item.by_default)

    def save_modal(self, event: ControlEvent) -> None:
        """Save this modal."""
        self.value.error_text = None

        if self.is_valid is False:
            self.update()
            return

        new_bonus = {
            "name": self.name.value,
            "value": self.value.value,
            "type": self.type.value,
            "by_default": self.by_default.value,
        }

        # if value changed create new rate
        if float(self.bonus_item.value) != float(new_bonus["value"]):
            self.bonus_item.state = 2
            self.bonus_item.change()

            self.new_bonus = self.money.add_bonus(new_bonus)
            self.page.close(self)
            return

        self.new_bonus = self.money.update_bonus(new_bonus, self.bonus_item)
        self.page.close(self)  # type: ignore
