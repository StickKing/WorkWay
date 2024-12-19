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
        self.db_path = self.get_db_path(debag=True)
        self.db = DataBase(str(self.db_path), use_datacls=True)

        self.money = Money(self, self.db)
        self.main = Main(self, self.db)
        self.settings = Settings(self, self.db)

    def get_db_path(self, *, debag: bool = False) -> Path:
        """Return db path."""
        if debag:
            db_path = Path.cwd() / "data"
        else:
            db_path = Path.cwd().parent.parent
            db_path = db_path / "workway_data"

        db_path.mkdir(exist_ok=True)
        return db_path / "work.db"

    def reinitialize_db(self):
        self.db.__class__._instances = {}  # type: ignore
        self.db = DataBase(str(self.db_path), use_datacls=True)

        for subcore in ("money", "main", "settings"):
            getattr(self, subcore).db = self.db
