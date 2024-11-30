"""Module contain create work view subcore."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from typing import Iterable

from .base import BaseCore


if TYPE_CHECKING:
    from workway.typings import TCompleteBonus
    from workway.typings import TCompleteRework

    from ..db.tables import BonusRow
    from ..db.tables import RateRow
    from ..db.tables import WorkRow


class Сalculation:
    """Сalculation work income money."""

    class RateСalculation:
        """Descriptor for calculating rate."""

        def __get__(
            self,
            obj: "Сalculation",
            objtype: None = None,
        ) -> float:
            self.calc = obj
            return self()

        def __call__(self) -> float:
            money = 0
            rate = self.calc.rate
            start_datetime = self.calc.start_datetime
            end_datetime = self.calc.end_datetime
            match rate.type:
                case "shift":
                    money += rate.value
                case "hours":
                    difference = end_datetime - start_datetime
                    hours = difference.seconds // 60 // 60
                    money += hours * rate.value
            return money

    class BonusСalculation:
        """Descriptor for calculating bonuses."""

        def __get__(
            self,
            obj: "Сalculation",
            objtype: None = None,
        ) -> float:
            self.calc = obj
            return self()

        def _calculate_fix_sum(
            self,
            bonuses: Iterable["BonusRow"] | map,
        ) -> float:
            """Calculate bonus with type 'fix'."""
            money = 0
            for bonus in bonuses:
                money += bonus.value
            return money

        def _calculate_percent(
            self,
            bonuses: Iterable[TCompleteBonus],
        ) -> float:
            """Calculate bonus with type 'percent'."""
            calculate_rate = self.calc.calculate_rate
            calculate_rework = self.calc.calculate_rework

            rate_with_rework = calculate_rate + calculate_rework

            bonuses_list = []

            for bonus in bonuses:
                if bonus["on_full_sum"]:
                    bonuses_list.append(
                        rate_with_rework / 100 * bonus["bonus"].value
                    )
                    continue
                bonuses_list.append(
                    calculate_rate / 100 * bonus["bonus"].value
                )
            return sum(bonuses_list)

        def __call__(self) -> float:
            """Calculate bonus money."""
            bonuses = self.calc.bonuses

            if not bonuses:
                return 0

            fix_bonuses = filter(
                lambda b: b["bonus"].type == "fix",
                bonuses,
            )
            percent_bonuses = filter(
                lambda b: b["bonus"].type == "percent",
                bonuses,
            )

            fix_sum = self._calculate_fix_sum(
                map(lambda b: b["bonus"], fix_bonuses),
            )

            percent = self._calculate_percent(
                percent_bonuses,
            )
            return fix_sum + percent

    class ReworkСalculation:
        """Descriptor for calculating rework."""

        def __get__(
            self,
            obj: "Сalculation",
            objtype: None = None,
        ) -> float:
            self.calc = obj
            return self()

        def __call__(self) -> float:
            start_datetime = self.calc.start_datetime
            end_datetime = self.calc.end_datetime
            rate = self.calc.rate
            rework = self.calc.rework
            money = 0
            if rework is None:
                return 0

            match rework["type"]:
                case "%":
                    difference = end_datetime - start_datetime
                    hours = difference.total_seconds() // 60 // 60
                    rework_hours = hours - rate.hours
                    money_percent = (rate.value / 100) * rework["value"]
                    money += rework_hours * money_percent
                case "sum":
                    money += rework["value"]
            return money

    rate_calc = RateСalculation()
    bonus_calc = BonusСalculation()
    rework_calc = ReworkСalculation()

    def __init__(
        self,
        core: "WorkMaker",
        rate: "RateRow",
        bonuses: Iterable[TCompleteBonus],
        start_datetime: datetime,
        end_datetime: datetime,
        rework: TCompleteRework | None = None,
    ) -> None:
        self.core = core
        self.rate = rate
        self.bonuses = bonuses
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.rework = rework

        # order is important
        self.calculate_rate = self.rate_calc
        self.calculate_rework = self.rework_calc
        self.calculate_bonus = self.bonus_calc

    def result(self) -> float:
        """Return completed money value."""
        return sum((
            self.calculate_rate,
            self.calculate_rework,
            self.calculate_bonus,
        ))


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
        bonuses: Iterable["BonusRow"] | map,
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
        bonuses: Iterable[TCompleteBonus],
        start_datetime: datetime,
        end_datetime: datetime,
        name: str | None = "",
        rework: TCompleteRework | None = None,
    ) -> None:
        """Save new work in db."""
        work_income = Сalculation(
            self,
            rate,
            bonuses,
            start_datetime,
            end_datetime,
            rework,
        )

        work_day = {
            "name": name,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "hours": 0,
            "rate_id": rate.id,
            "value": work_income.result(),
        }
        self.db.work.add(work_day)

        work: WorkRow = self.db.work.get(**work_day)
        self._save_work_bonuses(
            work.id,
            map(lambda b: b["bonus"], bonuses),
        )
