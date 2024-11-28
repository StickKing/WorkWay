"""Module contains tables cls."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum

from lildb import Table
from lildb.rows import _RowDataClsMixin


__all__ = (
    "RateTable",
    "RateRow",
    "BonusTable",
    "BonusRow",
)


class RateType(Enum):
    """Rate enum type."""

    shift = "Обычная"
    hour = "Почасовая"


@dataclass(slots=True)
class RateRow(_RowDataClsMixin):

    id: int
    by_default: bool
    name: str
    value: float
    type: str
    hours: int
    state: int

    # Required fields for row-cls
    table: Table
    changed_columns: set = field(default_factory=lambda: set())  # type: ignore
    types = RateType


class RateTable(Table):
    """Rage table."""

    row_cls = RateRow


class BonusType(Enum):
    """Bonus enum type."""

    fix = "Фикс. сумма"
    percent = "Процентная"


@dataclass(slots=True)
class BonusRow(_RowDataClsMixin):

    id: int
    by_default: bool
    name: str
    value: float
    state: int
    type: str

    # Required fields for row-cls
    table: Table
    changed_columns: set = field(default_factory=lambda: set())  # type: ignore

    types = BonusType


class BonusTable(Table):
    """Bonus table."""

    row_cls = BonusRow


@dataclass(slots=True)
class WorkRow(_RowDataClsMixin):

    id: int
    name: str
    start_datetime: str
    end_datetime: str
    hours: int
    rate_id: int
    value: float
    json: str

    # Required fields for row-cls
    table: Table
    changed_columns: set = field(default_factory=lambda: set())  # type: ignore

    @property
    def start_dttm(self) -> datetime:
        """Return datetime from timestamp."""
        return datetime.fromisoformat(self.start_datetime)

    @start_dttm.setter
    def start_dttm(self, value: datetime) -> None:
        """Change start datetime."""
        self._start_datetime = value

    @property
    def end_dttm(self) -> datetime:
        """Return datetime from timestamp."""
        return datetime.fromisoformat(self.end_datetime)

    @end_dttm.setter
    def end_dttm(self, value: datetime) -> None:
        """Change start datetime."""
        self._end_datetime = value

    @property
    def rate(self) -> RateRow:
        """Return relation rate."""
        return self.table.db.rate.get(id=self.rate_id)  # type: ignore

    @property
    def bonuses(self) -> list[BonusRow]:
        """Return relation bonuses."""
        work_bonuses = self.table.db.work_bonus.select(
            work_id=self.id
        )
        stmt = ", ".join(
            str(work_bonus.bonus_id)
            for work_bonus in work_bonuses
        )
        return self.table.db.bonus.select(condition=f"id IN ({stmt})")


class WorkTable(Table):
    """Work table."""

    row_cls = WorkRow
