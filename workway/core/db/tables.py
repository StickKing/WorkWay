"""Module contains tables cls."""
from dataclasses import dataclass

from lildb import Table
from lildb.rows import _RowDataClsMixin


@dataclass
class RateRow(_RowDataClsMixin):

    _by_default: float

    def by_default(self) -> bool:
        """By default change to bool."""
        return bool(self._by_default)


class RateTable(Table):
    """Rage table."""

    row_cls = RateRow
