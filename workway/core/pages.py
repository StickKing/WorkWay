"""Module contain pages logic."""
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal


if TYPE_CHECKING:
    from .core import Core
    from .db import DataBase


class Page(ABC):
    """Page cls with all logic."""
    
    def __init__(self, core, db) -> None:
        """Initialize."""
        self.db: DataBase = db
        self.core: Core = core
        

class Money(Page):
    
    def add_rate(self, data: dict) -> None:
        """Add new rate."""
        if data["type"]:
            data.pop("hours")
        data["name"] = data["name"] or data["value"]
        data["type"] = "hour" if data["type"] else "shift"
        self.db.rate.insert(data)
    
    def all_rate(self) -> list:
        """Getting rate."""
        return self.db.rate.all()
    
    def all_bonus(self) -> list:
        """Getting rate."""
        return self.db.rate.all()