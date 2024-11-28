"""Module contain component with business logic."""
from __future__ import annotations

import sqlite3
from sqlite3 import OperationalError
from typing import Any
from typing import Callable
from typing import MutableMapping
from typing import Sequence

from lildb import DB
from lildb.column_types import Integer
from lildb.column_types import Real
from lildb.column_types import Text
from lildb.enumcls import ResultFetch

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
        self.prepare_db()

    def prepare_db(self):
        """Prepare data base for work."""
        self.initialize_db()
        try:
            self.migrations()
        except OperationalError:
            pass
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
                "type": Text(default="fix"),
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
                "json": Text(),
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

    def migrations(self) -> None:
        """Migrations for data base."""
        self.execute(
            "ALTER TABLE Work ADD COLUMN json TEXT NOT NULL DEFAULT ''",
        )
        self.execute(
            "ALTER TABLE Bonus ADD COLUMN type TEXT NOT NULL DEFAULT 'fix'",
        )

    def execute(
        self,
        query: str,
        parameters: MutableMapping | Sequence = (),
        *,
        many: bool = False,
        size: int | None = None,
        result: ResultFetch | None = None,
    ) -> list[Any] | None:
        """Single execute to simplify it.

        Args:
            query (str): sql query
            parameters (MutableMapping | Sequence): data for executing.
            Defaults to ().
            many (bool): flag for executemany operation. Defaults to False.
            size (int | None): size for fetchmany operation. Defaults to None.
            result (ResultFetch | None): enum for fetch func. Defaults to None.

        Returns:
            list[Any] or None

        """
        command = query.partition(" ")[0].lower()
        cursor = self.connect.cursor()
        if many:
            cursor.executemany(query, parameters)
        else:
            cursor.execute(query, parameters)

        if command in {
            "insert",
            "delete",
            "update",
            "create",
            "drop",
            "alter",
        }:
            self.connect.commit()

        # Check result
        if result is None:
            return None

        ResultFetch(result)

        result_func: Callable = getattr(cursor, result.value)

        if result.value == "fetchmany":
            return result_func(size=size)
        return result_func()

# if __name__ == "__main__":
#     core = Core("local.db")
