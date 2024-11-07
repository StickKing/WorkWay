
from collections import UserString
from typing import Any, Literal, MutableMapping, Sequence
from lildb.operations import CreateTable
from lildb.column_types import BaseType


TOption = Literal["set null", "cascade", "restrict", "set default"]


class ForeignKey(UserString):
    """Foreign key constraint."""

    def __init__(
        self,
        column: str,
        table: str,
        reference_column: str,
        on_delete: TOption | None = None,
        on_update: TOption | None = None,
    ) -> None:
        """Initialize."""
        self.column = column
        self.table = table
        self.reference_column = reference_column
        self.on_delete = on_delete
        self.on_update = on_update
        super().__init__("FOREIGN KEY(`{}`) REFERENCES `{}`(`{}`)")

    def __call__(self) -> Any:
        """Create command."""
        stmt = self.data.format(
            self.column,
            self.table,
            self.reference_column,
        )
        if self.on_delete:
            stmt += f" ON DELETE {self.on_delete}"
        if self.on_update:
            stmt += f" ON UPDATE {self.on_update}"
        return stmt


class CreateTable(CreateTable):
    """With foreign keys."""

    def __call__(
        self,
        table_name: str,
        columns: Sequence[str] | MutableMapping[str, Any],
        table_primary_key: Sequence[str] | None = None,
        foreign_keys: Sequence[ForeignKey] | None = None,
        *,
        if_not_exists: bool = True,
    ) -> None:
        """Create table in DB.

        Args:
            table_name (str): table name
            columns (Sequence[str] | MutableMapping[str, str]): column name or
            dict column with column types
            table_primary_key (Sequence[str] | None): set table primary key.
            Defaults to None.
            if_not_exists (bool): use 'if not exists' in query.
            Defaults to True.

        Raises:
            TypeError: Incorrect type for columns
            TypeError: Incorrect type for column item

        """
        query = f"{self.query(if_not_exists=if_not_exists)}`{table_name}`"

        if not isinstance(columns, (Sequence, MutableMapping)):
            msg = "Incorrect type for columns"
            raise TypeError(msg)

        primary_key: str = ""

        if isinstance(table_primary_key, Sequence):
            primary_key = ", PRIMARY KEY(" + ",".join(
                _ for _ in table_primary_key
            ) + ")"

        if foreign_keys:
            keys = ", ".join(
                key()
                for key in foreign_keys
            )
            primary_key += keys if primary_key else ", " + keys

        if (
            isinstance(columns, Sequence) and
            all(isinstance(_, str) for _ in columns)
        ):
            columns_query = ", ".join(columns)
            query = f"{query}({columns_query}{primary_key})"
            self.db.execute(query)
            self.db.initialize_tables()
            return

        if (
            not isinstance(columns, MutableMapping) or
            not all(isinstance(_, BaseType) for _ in columns.values())
        ):
            msg = "Incorrect type for column item"
            raise TypeError(msg)

        columns_query = ", ".join(
            f"`{key}` {value}"
            for key, value in columns.items()
        )

        query = f"{query} ({columns_query}{primary_key})"

        self.db.execute(query)
        self.db.initialize_tables()
