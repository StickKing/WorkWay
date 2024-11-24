"""Module contain component with business logic."""
from __future__ import annotations

import sqlite3
from typing import Any

from lildb import DB
from lildb.column_types import Integer
from lildb.column_types import Real
from lildb.column_types import Text

from .column import ForeignKey
from .operation import CreateTable
from .tables import BonusTable
from .tables import RateTable
from .tables import WorkTable


class DataBase(DB):
    """Component with business logic."""

    rate = RateTable("rate")
    bonus = BonusTable("bonus")
    work = WorkTable("work")

    def __init__(
        self,
        path: str,
        *,
        use_datacls: bool = True,
        **connect_params: Any,
    ) -> None:
        self.path = path
        self.connect: sqlite3.Connection = sqlite3.connect(
            path,
            **connect_params,
        )
        self.use_datacls = use_datacls
        self.table_names: set = set()
        self.create_table = CreateTable(self)
        self.initialize_db()
        self.initialize_tables()

    def initialize_db(self) -> None:
        """Create all tables."""
        self.create_table(
            "Rate",
            {
                "id": Integer(primary_key=True),
                "name": Text(default=""),
                "value": Real(default=0),  # type: ignore
                "by_default": Real(default=0),  # type: ignore
                "type": Text(default="shift"),
                "hours": Integer(default=8),
                "state": Integer(default=1),
            }
        )
        self.create_table(
            "Bonus",
            {
                "id": Integer(primary_key=True),
                "name": Text(default=""),
                "value": Real(default=0),  # type: ignore
                "by_default": Real(default=0),  # type: ignore
                "state": Integer(default=1),
            }
        )
        self.create_table(
            "Work",
            {
                "id": Integer(primary_key=True),
                "name": Text(default=""),
                "start_datetime": Text(),
                "end_datetime": Text(),
                "hours": Integer(),
                "rate_id": Integer(),
                "value": Real(),
            },
            foreign_keys=(
                ForeignKey("rate_id", "Rate", "id"),
            )
        )
        self.create_table(
            "Work_Bonus",
            {
                "work_id": Integer(),
                "bonus_id": Integer(),
            },
            foreign_keys=(
                ForeignKey("work_id", "Work", "id", on_delete="cascade"),
                ForeignKey("bonus_id", "Bonus", "id", on_delete="cascade"),
            )
        )

# if __name__ == "__main__":
#     core = Core("local.db")
