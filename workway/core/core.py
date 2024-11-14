"""Module contain core."""
from __future__ import annotations

from typing import Any

from .db import DataBase
from .pages import Money


class Core:
    
    _instance = None
    
    def __new__(cls: type[Core], *args: Any, **kwargs: Any) -> Core:
        """Singleton."""
        if cls._instance is not None:
            return cls._instance
        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db = DataBase("work.db", use_datacls=True)
        self.money = Money(self, self.db)
        