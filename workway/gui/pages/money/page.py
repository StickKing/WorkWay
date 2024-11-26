"""Module contain rate and bonus page."""
from functools import cached_property
from typing import TYPE_CHECKING

from flet import BorderRadius
from flet import ButtonStyle
from flet import Column
from flet import Container
from flet import ControlEvent
from flet import IconButton
from flet import MainAxisAlignment
from flet import Margin
from flet import Padding
from flet import Row
from flet import ScrollMode
from flet import Text
from flet import TextThemeStyle
from flet import colors
from flet import icons

from .modals import BonusModal
from .modals import RateModal
from .tiles import BonusTile
from .tiles import RateTile


if TYPE_CHECKING:
    from workway.core.subcores import Money


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
            Container(
                content=Column([
                    Text(
                        "Ставки 💰",
                        theme_style=TextThemeStyle.TITLE_LARGE,
                    ),
                    self.rates,
                ]),
                margin=Margin(left=0, top=0, right=0, bottom=10),
                padding=Padding(left=15, top=10, right=0, bottom=10),
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=BorderRadius(
                    top_left=0,
                    top_right=0,
                    bottom_left=12,
                    bottom_right=12,
                ),
            ),
            Container(
                content=Column([
                    Text(
                        "Надбавки 💸",
                        theme_style=TextThemeStyle.TITLE_LARGE,
                    ),
                    self.bonuses,
                ]),
                bgcolor=colors.SURFACE_VARIANT,
                padding=Padding(left=15, top=10, right=0, bottom=10),
                border_radius=BorderRadius(
                    top_left=12,
                    top_right=12,
                    bottom_left=0,
                    bottom_right=0,
                ),
            ),
        ]

    def add_rate(self, event: ControlEvent) -> None:
        """Create new rate obj."""
        modal: RateModal = event.control

        if modal.new_rate is None:
            return

        self.rates.controls.insert(
            -1,
            RateTile(self.money, modal.new_rate),
        )
        self.update()

    @cached_property
    def rates(self) -> Column:
        rates = [
            RateTile(self.money, rate)
            for rate in self.money.all_rate()
        ]
        add_button = IconButton(
            icon=icons.ADD,
            style=ButtonStyle(bgcolor=colors.BLACK),
            on_click=lambda e: self.page.open(  # type: ignore
                RateModal(self.money, self.add_rate)
            ),
            width=50,
            height=50,
        )
        return Column(
            controls=[
                *rates,
                Row(
                    [
                        add_button,
                    ],
                    alignment=MainAxisAlignment.CENTER,
                )
            ],
        )

    def add_bonus(self, event: ControlEvent) -> None:
        """Create new bonus obj."""
        modal: BonusModal = event.control

        if modal.new_bonus is None:
            return

        self.bonuses.controls.insert(
            -1,
            BonusTile(self.money, modal.new_bonus),
        )
        self.update()

    @cached_property
    def bonuses(self) -> Column:
        bonuses = [
            BonusTile(self.money, bonus)
            for bonus in self.money.all_bonus()
        ]
        add_button = IconButton(
            icon=icons.ADD,
            style=ButtonStyle(bgcolor=colors.BLACK),
            on_click=lambda e: self.page.open(  # type: ignore
                BonusModal(self.money, self.add_bonus)
            ),
            width=50,
            height=50,
        )
        return Column(
            controls=[
                *bonuses,
                Row(
                    [
                        add_button,
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
            ],
        )
