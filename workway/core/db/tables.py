"""Module contains tables cls."""
from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum

from lildb import Table
from lildb.rows import _RowDataClsMixin

from workway.typings import TCompleteOtherIncome

from .operation import UpdateFixed


__all__ = (
    "RateTable",
    "RateRow",
    "BonusTable",
    "BonusRow",
)


class PretifyMoneyMixin:
    """Pretify money."""

    value: float

    @property
    def pretify_money(self) -> str:
        """Prepare string money."""
        money = str(round(self.value, 2))
        total, cent = money.split(".")
        if cent == "0":
            money = total
        return f"{money} руб."


class TypeMixin:
    """Type method mixin."""

    types: type[Enum]
    type: str

    @property
    def type_name(self) -> str:
        """String type name."""
        return getattr(self.types, self.type).value


class RateType(Enum):
    """Rate enum type."""

    shift = "Обычная"
    hour = "Почасовая"


@dataclass(slots=True)
class RateRow(_RowDataClsMixin, PretifyMoneyMixin, TypeMixin):

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

    @property
    def default(self) -> bool:
        """Is rate use default."""
        return bool(self.by_default)


class RateTable(Table):
    """Rage table."""

    row_cls = RateRow

    update = UpdateFixed


class BonusType(Enum):
    """Bonus enum type."""

    fix = "Фикс. сумма"
    percent = "Процентная"


@dataclass(slots=True)
class BonusRow(_RowDataClsMixin, TypeMixin):

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

    @property
    def default(self) -> bool:
        """Is rate use default."""
        return bool(self.by_default)

    @property
    def pretify_money(self) -> str:
        """Prepare string money."""
        money = str(self.value)
        total, cent = money.split(".")
        if cent == "0":
            money = total
        if self.type == "fix":
            return f"{money} руб."
        return f"{money} %"


class BonusTable(Table):
    """Bonus table."""

    row_cls = BonusRow

    update = UpdateFixed


@dataclass(slots=True)
class WorkRow(_RowDataClsMixin, PretifyMoneyMixin):

    id: int
    name: str
    start_datetime: str
    end_datetime: str
    hours: int
    rate_id: int
    rework_id: int
    state: int
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
    def rework(self) -> RateRow:
        """Return relation rate."""
        return self.table.db.rework.get(id=self.rework_id)  # type: ignore

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

    @property
    def other_income(self) -> list[TCompleteOtherIncome]:
        """Return other income."""
        json_data = json.loads(self.json)
        return json_data["other_income"]


class WorkTable(Table):
    """Work table."""

    row_cls = WorkRow

    update = UpdateFixed


@dataclass(slots=True)
class WorkBonus(_RowDataClsMixin):

    work_id: int
    bonus_id: int
    on_full_sum: bool

    # Required fields for row-cls
    table: Table
    changed_columns: set = field(default_factory=lambda: set())  # type: ignore


class Work_Bonus(Table):
    """Work table."""

    row_cls = WorkBonus

    update = UpdateFixed
