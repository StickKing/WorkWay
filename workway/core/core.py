"""Module contain core."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .db import DataBase
from .subcores import Main
from .subcores import Money
from .subcores import Settings


class Core:

    _instance = None

    def __new__(cls: type[Core], *args: Any, **kwargs: Any) -> Core:
        """Singleton."""
        if cls._instance is not None:
            return cls._instance
        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        db_path = Path.cwd().parent.parent
        db_path = db_path / "workway_data"
        # db_path = Path.cwd().parent
        db_path.mkdir(exist_ok=True)
        self.db = DataBase(f"{db_path}/work.db", use_datacls=True)
        self.money = Money(self, self.db)
        self.main = Main(self, self.db)
        self.settings = Settings(self, self.db)
