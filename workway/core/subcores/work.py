"""Module contain create work view subcore."""
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable

from .base import BaseCore


if TYPE_CHECKING:
    from ..db.tables import BonusRow
    from ..db.tables import RateRow


class Сalculation:

    class RateСalculation:
        """Descriptor for calculating rate."""

        def __set_name__(self, owner: type["Сalculation"], name: str) -> None:
            self.money = 0

        def __get__(self, obj: "Сalculation"):
            self.calc = obj
            return self

        def __call__(self) -> Any:
            rate = self.calc.rate
            start_datetime = self.calc.start_datetime
            end_datetime = self.calc.end_datetime
            match rate.type:
                case "shift":
                    self.money += rate.value
                case "hours":
                    difference = end_datetime - start_datetime
                    hours = difference.seconds // 60 // 60
                    self.money += hours * rate.value
            return self.money

    class BonusСalculation:
        """Descriptor for calculating bonuses."""

        def __get__(self, obj: "Сalculation"):
            self.calc = obj
            return self

        def calculate_fix_sum(self, bonuses: Iterable["BonusRow"]) -> float:
            money = 0
            for bonus in bonuses:
                money += bonus.value
            return money

    def __init__(
        self,
        core: "WorkMaker",
        rate: "RateRow",
        bonuses: Iterable[dict[str, Any | bool]],
        start_datetime: datetime,
        end_datetime: datetime,
        name: str | None = "",
        rework: dict[str, int | float] | None = None,
    ) -> None:
        self.core = core
        self.rate = rate
        self.bonuses = bonuses
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.name = name
        self.rework = rework


class WorkMaker(BaseCore):
    """Subcore for work maker view page."""

    __slots__ = ("db", "core")

    def get_rates(self) -> dict[str, "RateRow"]:
        """Get all rates for create view."""
        rates = self.db.rate.select(state=1)
        rates.sort(key=lambda e: -e.by_default)
        return {
            str(rate.id): rate
            for rate in rates
        }

    def get_bonuses(self) -> list:
        """Get all bonuses for create view."""
        return self.db.bonus.select(state=1)

    def _save_work_bonuses(
        self,
        work_id: int,
        bonuses: Iterable["BonusRow"],
    ) -> None:
        """Save bonuses."""
        for bonus in bonuses:
            self.db.work_bonus.add({
                "work_id": work_id,
                "bonus_id": bonus.id,
            })

    def save_work(
        self,
        rate: "RateRow",
        bonuses: Iterable[dict[str, Any | bool]],
        start_datetime: datetime,
        end_datetime: datetime,
        name: str | None = "",
        rework: dict[str, int | float] | None = None,
    ) -> None:
        """Save new work in db."""
        # Rate
        money_value = 0
        match rate.type:
            case "shift":
                money_value += rate.value
            case "hours":
                hours = (end_datetime - start_datetime).seconds // 60 // 60
                money_value += hours * rate.value

        # Rework
        if rework:
            match next(rework.__iter__()):
                case "%":
                    difference = end_datetime - start_datetime
                    hours = difference.total_seconds() // 60 // 60
                    rework_hours = hours - rate.hours
                    money_percent = (rate.value / 100) * rework["%"]
                    money_value += rework_hours * money_percent
                case "sum":
                    money_value += rework["sum"]

        # Bonus
        for bonus in bonuses:
            money_value += bonus.value

        work_day = {
            "name": name,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "hours": 0,
            "rate_id": rate.id,
            "value": money_value,
        }
        self.db.work.add(work_day)

        work = self.db.work.get(**work_day)
        self._save_work_bonuses(
            work.id,  # type: ignore
            bonuses,
        )
