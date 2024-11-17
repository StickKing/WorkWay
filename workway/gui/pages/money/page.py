"""Module contain rate and bonus page."""
from functools import cached_property
from typing import TYPE_CHECKING

from flet import Column
from flet import ControlEvent
from flet import ElevatedButton
from flet import ScrollMode
from flet import Text

from .modals import BonusModal
from .modals import RateModal
from .tiles import BonusTile
from .tiles import RateTile


if TYPE_CHECKING:
    from workway.core.pages import Money


__all__ = (
    "MoneyPage",
)


class MoneyPage(Column):
    """Money page contain controls for CRUD rate and bonus."""

    def __init__(self, money) -> None:
        """Initialize."""
        self.money: Money = money
        super().__init__(
            controls=self.get_controls(),
            scroll=ScrollMode.HIDDEN,
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
        modal: RateModal = event.control

        if modal.new_rate is None:
            return

        self.rates.controls.insert(-1, RateTile(self.money, modal.new_rate))
        self.update()

    @cached_property
    def rates(self) -> Column:
        rates = [
            RateTile(self.money, rate)
            for rate in self.money.all_rate()
        ]
        add_button = ElevatedButton(
            "Добавить ставку",
            on_click=lambda e: self.page.open(  # type: ignore
                RateModal(self.money, self.add_rate)
            ),
        )
        return Column(
            controls=[
                *rates,
                add_button,
            ],
        )

    def add_bonus(self, event: ControlEvent) -> None:
        """Create new bonus obj."""
        modal: BonusModal = event.control

        if modal.new_bonus is None:
            return

        self.bonuses.controls.insert(-1, RateTile(self.money, modal.new_bonus))
        self.update()

    @cached_property
    def bonuses(self) -> Column:
        bonuses = [
            BonusTile(self.money, bonus)
            for bonus in self.money.all_bonus()
        ]
        return Column(
            controls=[
                *bonuses,
                ElevatedButton(
                    "Добавить надбавку",
                    on_click=lambda e: self.page.open(  # type: ignore
                        BonusModal(self.money, self.add_bonus)
                    ),
                )
            ],
        )
