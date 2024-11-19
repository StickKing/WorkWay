"""Module contain pages logic."""
from abc import ABC
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from .core import Core
    from .db import DataBase


class BaseCore(ABC):
    """Page cls with all logic."""

    def __init__(self, core, db) -> None:
        """Initialize."""
        self.db: DataBase = db
        self.core: Core = core


class Money(BaseCore):
    """Realize logic for money page."""

    def prepare_insert_data(self, data: dict) -> None:
        if data["type"]:
            data.pop("hours")
        data["name"] = data["name"] or data["value"]
        data["type"] = "hour" if data["type"] else "shift"

    def add_rate(self, data: dict) -> None:
        """Add new rate."""
        self.prepare_insert_data(data)
        self.db.rate.insert(data)
        return self.db.rate.get(**data)

    def add_bonus(self, data: dict) -> None:
        """Add new bonus."""
        data["name"] = data["name"] or data["value"]
        self.db.bonus.insert(data)
        return self.db.bonus.get(**data)

    def all_rate(self) -> list:
        """Getting rate."""
        return self.db.rate.select(state=1)

    def all_bonus(self) -> list:
        """Getting rate."""
        return self.db.bonus.select(state=1)

    def update_item(self, data: dict, item) -> None:
        """Update rate or bonus."""
        if data.get("type"):
            self.prepare_insert_data(data)

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


class Main(BaseCore):

    def get_default_rate(self) -> Any:
        """Return default rate."""
        return self.db.rate.get(by_default=1)

    def get_rates(self):
        """Get all rates for create view."""
        return self.db.rate.select(state=1)
