"""Module contain rate and bonus page."""
from typing import TYPE_CHECKING

from flet import ControlEvent
from flet import Icon
from flet import ListTile
from flet import PopupMenuButton
from flet import PopupMenuItem
from flet import Text
from flet import icons

from ..common import PresentatorSheet
from .modals import UpdateBonusModal
from .modals import UpdateRateModal


if TYPE_CHECKING:
    from workway.core.db.tables import BonusRow
    from workway.core.db.tables import RateRow
    from workway.core.subcores import Money


class RateTile(ListTile):
    """Rate gui element."""

    def __init__(self, core: "Money", rate: "RateRow") -> None:
        self.core = core
        self.rate = rate
        super().__init__(
            leading=Icon(icons.ATTACH_MONEY),
            title=Text(self.rate.name),
            subtitle=Text(str(self.rate.pretify_money)),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(
                        text="Изменить",
                        on_click=self.open_update_view,
                    ),
                    PopupMenuItem(
                        text="Удалить",
                        on_click=self.delete,
                    ),
                ],
            ),
            on_click=lambda e: self.page.open(
                PresentatorSheet(
                    self.rate,
                    {
                        "Наименование": "name",
                        "Тип": "type_name",
                        "Сумма": "pretify_money",
                        "По умолчанию": "default",
                    }
                ),
            ),
        )

    def delete(self, event: ControlEvent) -> None:
        """Delete rate from db and gui."""
        self.core.delete_rate(self.rate.id)
        self.parent.controls.remove(self)
        self.parent.update()

    def update_rate(self, view: UpdateRateModal) -> None:
        """Update rate item after update."""
        if view.new_rate is None:
            return
        self.rate = view.new_rate
        self.title.value = self.rate.name
        self.subtitle.value = self.rate.value
        self.update()

    def open_update_view(self, event: ControlEvent) -> None:
        """Open update modal view."""
        self.page.views.append(  # type: ignore
            UpdateRateModal(
                self.core,
                self.rate,
                on_dismiss=self.update_rate,
            ),
        )
        self.page.update()


class BonusTile(ListTile):
    """Bonus gui element."""

    def __init__(self, core: "Money", bonus: "BonusRow") -> None:
        self.core = core
        self.bonus = bonus
        super().__init__(
            leading=Icon(icons.ATTACH_MONEY),
            title=Text(self.bonus.name),
            subtitle=Text(str(self.bonus.pretify_money)),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(
                        text="Изменить",
                        on_click=self.open_update_view,
                    ),
                    PopupMenuItem(
                        text="Удалить",
                        on_click=self.delete,
                    ),
                ],
            ),
            on_click=lambda e: self.page.open(
                PresentatorSheet(
                    self.bonus,
                    {
                        "Наименование": "name",
                        "Тип": "type_name",
                        "Сумма": "pretify_money",
                        "По умолчанию": "default",
                    }
                ),
            ),
        )

    def delete(self, event: ControlEvent) -> None:
        """Delete rate from db and gui."""
        self.bonus.state = 2
        self.bonus.change()
        self.parent.controls.remove(self)
        self.parent.update()

    def update_bonus(self, view: UpdateBonusModal) -> None:
        """Update rate item after update."""
        if view.new_bonus is None:
            return
        self.bonus = view.new_bonus
        self.title.value = self.bonus.name
        self.subtitle.value = self.bonus.value
        self.update()

    def open_update_view(self, event: ControlEvent) -> None:
        """Open update bonus view."""
        self.page.views.append(
            UpdateBonusModal(
                self.core,
                self.bonus,
                on_dismiss=self.update_bonus,
            ),
        )
        self.page.update()
