"""Module contain rate and bonus page."""
from typing import TYPE_CHECKING

from flet import ControlEvent
from flet import ListTile
from flet import PopupMenuButton
from flet import PopupMenuItem
from flet import Text
from flet import icons

from .modals import UpdateBonusModal
from .modals import UpdateRateModal


if TYPE_CHECKING:
    from workway.core.pages import Money


class RateTile(ListTile):
    """Rate gui element."""

    def __init__(self, money, rate) -> None:
        self.money: Money = money
        self.rate = rate
        super().__init__(
            leading=Text("💰"),
            title=Text(self.rate.name),
            subtitle=Text(self.rate.value),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(
                        text="Изменить",
                        on_click=lambda e: self.page.open(
                            UpdateRateModal(
                                self.money,
                                self.rate,
                                on_dismiss=self.update_rate,
                            ),
                        ),
                    ),
                    PopupMenuItem(
                        text="Удалить",
                        on_click=self.delete,
                    ),
                ],
            ),
        )

    def delete(self, event: ControlEvent) -> None:
        """Delete rate from db and gui."""
        self.money.delete_rate(self.rate.id)
        self.parent.controls.remove(self)
        self.parent.update()

    def update_rate(self, event: ControlEvent) -> None:
        """Update rate item after update."""
        modal: UpdateRateModal = event.control
        self.rate = modal.new_rate
        self.title.value = self.rate.name
        self.subtitle.value = self.rate.value
        self.update()


class BonusTile(ListTile):
    """Bonus gui element."""

    def __init__(self, money, bonus) -> None:
        self.money: Money = money
        self.bonus = bonus
        super().__init__(
            leading=Text("💸"),
            title=Text(self.bonus.name),
            subtitle=Text(self.bonus.value),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(
                        text="Изменить",
                        on_click=lambda e: self.page.open(
                            UpdateBonusModal(
                                self.money,
                                self.bonus,
                                on_dismiss=self.update_bonus,
                            ),
                        ),
                    ),
                    PopupMenuItem(
                        text="Удалить",
                        on_click=self.delete,
                    ),
                ],
            ),
        )

    def delete(self, event: ControlEvent) -> None:
        """Delete rate from db and gui."""
        self.bonus.state = 2
        self.bonus.change()
        self.parent.controls.remove(self)
        self.parent.update()

    def update_bonus(self, event: ControlEvent) -> None:
        """Update rate item after update."""
        modal: UpdateBonusModal = event.control
        self.bonus = modal.new_rate
        self.title.value = self.bonus.name
        self.subtitle.value = self.bonus.value
        self.update()
