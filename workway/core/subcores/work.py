"""Module contain create work view subcore."""
from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable

from typing_extensions import Self

from .base import BaseCore


if TYPE_CHECKING:
    from workway.typings import DataTableDict
    from workway.typings import TCompleteBonus
    from workway.typings import TCompleteOtherIncome
    from workway.typings import TCompleteRework

    from ..db.tables import BonusRow
    from ..db.tables import RateRow
    from ..db.tables import WorkRow


class Сalculation:
    """Сalculation work income money."""

    __slots__ = (
        "core",
        "rate",
        "bonuses",
        "start_datetime",
        "end_datetime",
        "rework",
        "other_income",
        "calculated_rate",
        "calculated_rework",
        "calculated_bonus",
        "calculated_other",
    )

    @classmethod
    def get_bonus_on_full_sum_ids(
        cls: type[Сalculation],
        work: "WorkRow",
    ) -> list["BonusRow"]:
        db = work.table.db
        work_bonuses = db.work_bonus.select(
            work_id=work.id,
            on_full_sum=1,
        )
        stmt = ", ".join(
            str(work_bonus.bonus_id)
            for work_bonus in work_bonuses
        )
        return db.bonus.select(condition=f"id IN ({stmt})")

    @classmethod
    def get_completed_rework(
        cls: type[Сalculation],
        work: "WorkRow",
    ) -> TCompleteRework | None:
        db = work.table.db
        rework: Any = None
        if work.rework_id is not None:
            rework = db.rework.get(id=work.rework_id)
            rework = {
                "value": rework.value,
                "type": rework.type,
            }
        return rework

    @classmethod
    def from_work(cls, core, work: "WorkRow") -> Self:
        """Create calculation obj from work."""
        bonus_full_sum_ids = cls.get_bonus_on_full_sum_ids(work)
        completed_bonuses: list[TCompleteBonus] = [
            {
                "bonus": bonus,
                "on_full_sum": True,
            } if bonus.id in bonus_full_sum_ids
            else {
                "bonus": bonus,
                "on_full_sum": False,
            }
            for bonus in work.bonuses
        ]

        return cls(
            core,
            work.rate,
            completed_bonuses,
            work.start_dttm,
            work.end_dttm,
            cls.get_completed_rework(work),
        )

    class RateСalculation:
        """Descriptor for calculating rate."""

        def fetch_data_table_view(self) -> "DataTableDict":
            """Fetch rate for data table."""
            rate = self.calc.rate
            type_name = "Ставка"
            if rate.type == "hour":
                type_name = "Ставка почасовая"
            return {
                "name": self.calc.rate.name,
                "type": type_name,
                "money": self.calc.calculated_rate,
            }

        def __get__(
            self,
            obj: "Сalculation",
            objtype: None = None,
        ) -> Self:
            self.calc = obj
            return self

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
        ) -> Self:
            self.calc = obj
            return self

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
            calculate_rate = self.calc.calculated_rate
            calculate_rework = self.calc.calculated_rework

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

        def fetch_data_table_view(self) -> list["DataTableDict"]:
            """Return bonus for view in data table."""
            calculate_rate = self.calc.calculated_rate
            calculate_rework = self.calc.calculated_rework

            rate_with_rework = calculate_rate + calculate_rework
            bonuses = self.calc.bonuses
            if not bonuses:
                return []

            percent_bonuses = filter(
                lambda b: b["bonus"].type == "percent",
                bonuses,
            )

            data_table_bonuses = []
            for bonus in percent_bonuses:
                if bonus["on_full_sum"]:
                    money = round(
                        rate_with_rework / 100 * bonus["bonus"].value,
                        2,
                    )
                    data_table_bonuses.append({
                        "name": bonus["bonus"].name,
                        "type": "Надбавка % с перераб.",
                        "money": money,
                    })
                    continue
                money = round(calculate_rate / 100 * bonus["bonus"].value, 2)
                data_table_bonuses.append({
                    "name": bonus["bonus"].name,
                    "type": "Надбавка %",
                    "money": money,
                })

            fix_bonuses = filter(
                lambda b: b["bonus"].type == "fix",
                bonuses,
            )
            for bonus in fix_bonuses:
                data_table_bonuses.append({
                    "name": bonus["bonus"].name,
                    "type": "Надбавка фикс.",
                    "money": bonus["bonus"].value,
                })
            return data_table_bonuses

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
        ) -> Self:
            self.calc = obj
            return self

        def fetch_data_table_view(self) -> DataTableDict | None:
            """Return rework for view in data table."""
            start_datetime = self.calc.start_datetime
            end_datetime = self.calc.end_datetime
            rate = self.calc.rate
            rework = self.calc.rework

            if rework is None:
                return None

            match rework["type"]:
                case "percent":
                    difference = end_datetime - start_datetime
                    hours = difference.total_seconds() // 60 // 60
                    rework_hours = hours - rate.hours
                    money_percent = (rate.value / 100) * rework["value"]
                    return {
                        "name": "Переработка",
                        "type": "{}%/час".format(rework["value"]),
                        "money": round(rework_hours * money_percent, 2),
                    }  # type: ignore
                case "fix":
                    return {
                        "name": "Переработка",
                        "type": "Фикс. сумма",
                        "money": rework["value"],
                    }  # type: ignore

        def __call__(self) -> float:
            start_datetime = self.calc.start_datetime
            end_datetime = self.calc.end_datetime
            rate = self.calc.rate
            rework = self.calc.rework
            money = 0
            if rework is None:
                return 0

            match rework["type"]:
                case "percent":
                    difference = end_datetime - start_datetime
                    hours = difference.total_seconds() // 60 // 60
                    rework_hours = hours - rate.hours
                    money_percent = (rate.value / 100) * rework["value"]
                    money += rework_hours * money_percent
                case "fix":
                    money += rework["value"]
            return money

    class OtherIncomeСalculation:
        """Other income money."""

        def __get__(
            self,
            obj: "Сalculation",
            objtype: None = None,
        ) -> Self:
            self.calc = obj
            return self

        def __call__(self) -> float:
            """Calculate money."""
            other_income = self.calc.other_income
            if not other_income:
                return 0
            money = 0
            for income in other_income:
                money += income["value"]
            return money

    rate_calc = RateСalculation()
    bonus_calc = BonusСalculation()
    rework_calc = ReworkСalculation()
    other_calc = OtherIncomeСalculation()

    def __init__(
        self,
        core: "WorkMaker",
        rate: "RateRow",
        bonuses: Iterable[TCompleteBonus],
        start_datetime: datetime,
        end_datetime: datetime,
        rework: TCompleteRework | None = None,
        other_income: list[TCompleteOtherIncome] | None = None,
    ) -> None:
        self.core = core
        self.rate = rate
        self.bonuses = bonuses
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.rework = rework
        self.other_income = other_income

        # order is important
        self.calculated_rate = self.rate_calc()
        self.calculated_rework = self.rework_calc()
        self.calculated_bonus = self.bonus_calc()
        self.calculated_other = self.other_calc()

    def result(self) -> float:
        """Return completed money value."""
        return sum((
            self.calculated_rate,
            self.calculated_rework,
            self.calculated_bonus,
            self.calculated_other,
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

    def get_work_bonuses_info(self, work: "WorkRow"):
        """Return work bonuses info for updating work."""
        return self.db.work_bonus.select(
            work_id=work.id
        )

    def _save_work_bonuses(
        self,
        work_id: int,
        bonuses: Iterable["TCompleteBonus"],
    ) -> None:
        """Save bonuses."""
        for bonus in bonuses:
            self.db.work_bonus.add({
                "work_id": work_id,
                "bonus_id": bonus["bonus"].id,
                "on_full_sum": bonus["on_full_sum"],
            })

    def save_work(
        self,
        rate: "RateRow",
        bonuses: Iterable[TCompleteBonus],
        start_datetime: datetime,
        end_datetime: datetime,
        name: str | None = "",
        rework: TCompleteRework | None = None,
        other_income: list[TCompleteOtherIncome] | None = None,
    ) -> None:
        """Save new work in db."""
        work_income = Сalculation(
            self,
            rate,
            bonuses,
            start_datetime,
            end_datetime,
            rework,
            other_income,
        )

        rework_id = None
        if rework:
            self.db.rework.add(rework)
            rework_id = self.db.rework.select(
                columns=["id"],
                condition="type = '{}' order by id desc limit 1".format(
                    rework["type"]
                ),
            )[0].id

        json_field = {"other_income": other_income}
        work_day = {
            "name": name,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "hours": 0,
            "rate_id": rate.id,
            "value": work_income.result(),
            "json": json.dumps(json_field),
            "rework_id": rework_id,
        }
        self.db.work.add(work_day)

        work: WorkRow = self.db.work.get(**work_day)
        self._save_work_bonuses(
            work.id,
            bonuses,
        )

    def update_item_by_dict(self, item, updated_dict: dict) -> None:
        """Update item attr."""
        for key, value in updated_dict.items():
            if str(getattr(item, key)) == str(value):
                continue
            setattr(item, key, value)

    def _update_work_bonuses(
        self,
        work_id: int,
        bonuses: Iterable["TCompleteBonus"],
    ) -> None:
        """Update work bonuses."""
        self.db.work_bonus.delete(work_id=work_id)
        rows = [
            {
                "work_id": work_id,
                "bonus_id": bonus["bonus"].id,
                "on_full_sum": bonus["on_full_sum"],
            }
            for bonus in bonuses
        ]
        if not rows:
            return
        self.db.work_bonus.add(rows)

    def update_work(
        self,
        updating_work: "WorkRow",
        rate: "RateRow",
        bonuses: Iterable[TCompleteBonus],
        start_datetime: datetime,
        end_datetime: datetime,
        name: str | None = "",
        rework: TCompleteRework | None = None,
        other_income: list[TCompleteOtherIncome] | None = None,
    ) -> None:
        """Save new work in db."""
        work_income = Сalculation(
            self,
            rate,
            bonuses,
            start_datetime,
            end_datetime,
            rework,
            other_income,
        )

        rework_id = None
        updating_rework = updating_work.rework
        if rework:
            if updating_rework:
                self.update_item_by_dict(updating_rework, rework)
                updating_rework.change()
                rework_id = updating_rework.id
            else:
                self.db.rework.add(rework)
                rework_id = self.db.rework.select(
                    columns=["id"],
                    condition="type = '{}' order by id desc limit 1".format(
                        rework["type"]
                    ),
                )[0].id
        elif not rework and updating_rework:
            updating_rework.delete()

        json_field = {"other_income": other_income}
        work_day = {
            "name": name,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "hours": 0,
            "rate_id": rate.id,
            "value": work_income.result(),
            "json": json.dumps(json_field),
            "rework_id": rework_id,
        }

        # self.update_item_by_dict(updating_work, work_day)
        self.db.work.update(work_day, id=updating_work.id)
        updating_work.change()

        self._update_work_bonuses(
            updating_work.id,
            bonuses,
        )
