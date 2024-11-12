from collections import UserString
from typing import Any
from typing import Literal


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
