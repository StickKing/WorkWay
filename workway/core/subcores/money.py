"""Module contain rate and bonus page subcore."""
from typing import TYPE_CHECKING

from .base import BaseCore


if TYPE_CHECKING:
    from ..db.tables import BonusRow
    from ..db.tables import RateRow


class Money(BaseCore):
    """Realize logic for money page."""

    __slots__ = ("db", "core")

    def prepare_insert_data(self, data: dict) -> None:
        if data["type"] == "shift":
            data.pop("hours")
        data["name"] = data["name"] or data["value"]

    def add_rate(self, data: dict) -> "RateRow":
        """Add new rate."""
        self.prepare_insert_data(data)
        self.db.rate.insert(data)
        return self.db.rate.get(**data)  # type: ignore

    def add_bonus(self, data: dict) -> "BonusRow":
        """Add new bonus."""
        data["name"] = data["name"] or data["value"]
        self.db.bonus.insert(data)
        return self.db.bonus.get(**data)  # type: ignore

    def all_rate(self) -> list["RateRow"]:
        """Getting rate."""
        return self.db.rate.select(state=1)

    def all_bonus(self) -> list["BonusRow"]:
        """Getting rate."""
        return self.db.bonus.select(state=1)

    def update_item(self, data: dict, item) -> "RateRow":
        """Update rate or bonus."""
        if data.get("type"):
            self.prepare_insert_data(data)

        for key, value in data.items():
            setattr(item, key, value)

        item.change()
        return item

    def update_bonus(self, data: dict, item: "BonusRow") -> "BonusRow":
        """Update bonus item."""
        for key, value in data.items():
            setattr(item, key, value)
        item.change()
        return item

    def delete_rate(self, id: int) -> None:
        """Delete curent rate, change state to 2 it is deleted status."""
        self.db.rate.update({"state": 2}, id=id)

    def delete_bonus(self, id: int) -> None:
        """Delete curent bonus, change state to 2 it is deleted status."""
        self.db.bonus.update({"state": 2}, id=id)
