
from typing import TYPE_CHECKING
from typing import Any
from typing import MutableMapping
from typing import Sequence

from lildb.column_types import BaseType
from lildb.operations import CreateTable
from lildb.operations import Update

from .column import ForeignKey


if TYPE_CHECKING:
    from lildb.operations import TOperator
    from lildb.operations import TQueryData


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


class UpdateFixed(Update):

    def _make_operator_query(
        self,
        data: "TQueryData",
        operator: "TOperator" = "AND",
        *,
        without_parameters: bool = False,
        null_is: bool = True,
    ) -> str:
        if operator.lower() not in {"and", "or", ","}:
            msg = "Incorrect operator."
            raise ValueError(msg)

        if not without_parameters:
            return f" {operator} ".join(
                f"{key} is NULL"
                if value is None and null_is
                else f"{key} = :{key}"
                for key, value in data.items()
            )

        return f" {operator} ".join(
            f"{key} is NULL"
            if value is None and null_is else
            f"{key} = '{value}'"
            if isinstance(value, str)
            else f"{key} = {value}"
            for key, value in data.items()
        )

    def __call__(
        self,
        data: "TQueryData",
        operator: "TOperator" = "AND",
        condition: str | None = None,
        **filter_by: Any,
    ) -> None:
        """Insert-query for current table."""
        if not isinstance(data, dict):
            msg = "Incorrect type for 'data.'"
            raise TypeError(msg)
        if not data:
            msg = "Argument 'data' do not be empty."
            raise ValueError(msg)
        query_coma = self._make_operator_query(
            data,
            operator=",",
            null_is=False,
        )
        query_operator = self._make_operator_query(
            filter_by,
            operator,
            without_parameters=True,
        )
        query = self.query + query_coma
        if filter_by:
            query = f"{query} WHERE {query_operator}"
            self.table.execute(query, data)  # type: ignore
            return
        if condition:
            query = f"{query} WHERE {condition}"
        self.table.execute(query, data)  # type: ignore
