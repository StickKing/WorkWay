"""Module contain component with business logic."""
from __future__ import annotations
from typing import Any
from lildb import DB
from lildb import Table
from lildb.column_types import Integer, Real, Text
from .db_component import ForeignKey, CreateTable


class RateTable(Table):
    """Rage table."""

    name = "Rate"

    def adding(self, data: dict[str, Any]) -> None:
        """Adding rate in table."""
        if data["type"]:
            data.pop("hours")
        data["type"] = "hour" if data["type"] else "shift"
        self.insert(data)


class Core(DB):
    """Component with business logic."""

    rate = RateTable()

    def __init__(
        self,
        path: str,
        *,
        use_datacls: bool = False,
        debug: bool = False,
        **connect_params: Any,
    ) -> None:
        super().__init__(path, use_datacls=use_datacls, debug=debug, **connect_params)
        self.create_table = CreateTable(self)
        self.initialize_db()

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
            }
        )
        self.create_table(
            "Bonus",
            {
                "id": Integer(primary_key=True),
                "name": Text(default=""),
                "value": Real(default=0),  # type: ignore
                "by_default": Real(default=0),  # type: ignore
            }
        )
        self.create_table(
            "WorkDay",
            {
                "id": Integer(primary_key=True),
                "name": Text(default=""),
                "value": Real(default=0),  # type: ignore
                "by_default": Real(default=0),  # type: ignore
                "rate_id": Integer(),
            },
            foreign_keys=(
                ForeignKey("rate_id", "Rate", "id"),
            )
        )
        self.create_table(
            "Work_Bonus",
            {
                "workday_id": Integer(),
                "bonus_id": Integer(),
            },
            foreign_keys=(
                ForeignKey("workday_id", "WorkDay", "id", on_delete="cascade"),
                ForeignKey("bonus_id", "Bonus", "id", on_delete="cascade"),
            )
        )

# if __name__ == "__main__":
#     core = Core("local.db")