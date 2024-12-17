"""Module contain rate and bonus page."""
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Callable

from flet import AppBar
from flet import Checkbox
from flet import ControlEvent
from flet import Dropdown
from flet import ElevatedButton
from flet import KeyboardType
from flet import MainAxisAlignment
from flet import Row
from flet import Text
from flet import TextField
from flet import View
from flet import dropdown

from workway.core.db.tables import BonusType
from workway.core.db.tables import RateType
from workway.gui.validators import is_number


if TYPE_CHECKING:
    from flet import Page

    from workway.core.subcores import Money


class ModalView(ABC):

    page: "Page"

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def is_valid(self) -> None:
        ...

    @abstractmethod
    def save_modal(self) -> None:
        ...

    def close_modal(self, event: ControlEvent) -> None:
        """Close this modal."""
        self.page.views.pop()
        self.page.update()


class RateModal(View, ModalView):
    """Rate modal for create new rate."""

    def __init__(
        self,
        core: "Money",
        on_dismiss: Callable | None = None,
    ) -> None:
        """Initialize."""
        self.on_dismiss = on_dismiss
        self.core: Money = core
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
            appbar=AppBar(
                title=Text("Создание ставки"),
            ),
            controls=[
                self.name,
                self.type,
                self.value,
                self.hours,
                self.by_default,
                Row([
                    ElevatedButton("Закрыть", on_click=self.close_modal),
                    ElevatedButton("Сохранить", on_click=self.save_modal),
                ]),
            ],
            vertical_alignment=MainAxisAlignment.CENTER,
            fullscreen_dialog=True,
            # on_dismiss=on_dismiss,
        )

    @property
    def is_valid(self) -> bool:
        """Validate data."""
        error_flag = True

        if not self.value.value:
            self.value.error_text = "Обязательное поле"
            error_flag = False

        if self.type.value == "shift" and not self.hours.value:
            self.hours.error_text = "Обязательное поле"
            error_flag = False

        if is_number(self.value.value) is False:
            self.value.error_text = "Должны быть только цифры"
            error_flag = False

        if not self.type.value and is_number(self.hours.value) is False:
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

        self.new_rate = self.core.add_rate(
            {
                "name": self.name.value,
                "value": self.value.value,
                "by_default": self.by_default.value,
                "hours": self.hours.value,
                "type": self.type.value,
            }
        )
        self.on_dismiss(self)
        self.close_modal(self)

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

    def __init__(
        self,
        core: "Money",
        rate_item,
        on_dismiss: Callable | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(core, on_dismiss)
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
        if (
            float(self.rate_item.value) != float(new_rate["value"]) or
            self.type.value != self.rate_item.type
        ):
            self.rate_item.state = 2
            self.rate_item.change()

            self.new_rate = self.core.add_rate(new_rate)
            self.on_dismiss(self)
            self.close_modal(self)
            return

        self.new_rate = self.core.update_item(new_rate, self.rate_item)
        self.on_dismiss(self)
        self.close_modal(self)


class BonusModal(View, ModalView):
    """Rate modal for create new rate."""

    def __init__(
        self,
        core: "Money",
        on_dismiss: Callable | None = None,
    ) -> None:
        """Initialize."""
        self.core: Money = core
        self.on_dismiss = on_dismiss
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
            appbar=AppBar(
                title=Text("Создание надбавки"),
            ),
            controls=[
                self.name,
                self.type,
                self.value,
                self.by_default,
                Row([
                    ElevatedButton("Закрыть", on_click=self.close_modal),
                    ElevatedButton("Сохранить", on_click=self.save_modal),
                ]),
            ],
        )

    @property
    def is_valid(self) -> bool:
        """Validate data."""
        error_flag = True

        if not self.value.value:
            self.value.error_text = "Обязательное поле"
            error_flag = False

        if is_number(self.value.value) is False:
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

        self.new_bonus = self.core.add_bonus(
            {
                "name": self.name.value,
                "value": self.value.value,
                "type": self.type.value,
                "by_default": self.by_default.value,
            }
        )
        self.on_dismiss(self)
        self.close_modal(self)

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
        if (
            float(self.bonus_item.value) != float(new_bonus["value"]) or
            self.type.value != self.bonus_item.type
        ):
            self.bonus_item.state = 2
            self.bonus_item.change()

            self.new_bonus = self.core.add_bonus(new_bonus)
            self.on_dismiss(self)
            self.close_modal(self)
            return

        self.new_bonus = self.core.update_bonus(new_bonus, self.bonus_item)
        self.on_dismiss(self)
        self.close_modal(self)
