"""Module contain pages logic."""
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal


if TYPE_CHECKING:
    from .db import DataBase


class Page(ABC):
    """Page cls with all logic."""
    
    def __init__(self, db) -> None:
        """Initialize."""
        self.db: DataBase = db
    
    @abstractmethod
    def add(self) -> Any:
        """Adding in data."""
        ...
    
    @abstractmethod
    def one(self) -> Any:
        """Get page data."""
        ...
    
    @abstractmethod
    def all(self) -> Any:
        """Get page data."""
        ...
        
    def filter(self, *args: Any, **kwargs: Any) -> Any:
        """Filtred page data."""
        raise NotImplementedError
        

class Money(Page):
    
    def add(self, data) -> None:
        """Add new rate."""
        if data["type"]:
            data.pop("hours")
        data["type"] = "hour" if data["type"] else "shift"
        self.db.rate.insert(data)
    
    def all(self) -> tuple:
        """Get all data."""
        return (self.db.rate.all(), self.db.bonus.all())
    
    def one(self):
        return None
    
    def filter(self, type: Literal["rate", "bonus"]):
        """Get data by type."""
        return 