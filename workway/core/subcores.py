"""Module contain pages logic."""
from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Iterable

from lildb.enumcls import ResultFetch

from .db.tables import BonusRow
from .db.tables import RateRow


if TYPE_CHECKING:
    from .core import Core
    from .db import DataBase
    from .db.tables import WorkRow


class BaseCore(ABC):
    """Page cls with all logic."""

    __slots__ = ("db", "core")

    def __init__(self, core, db) -> None:
        """Initialize."""
        self.db: DataBase = db
        self.core: Core = core


class Money(BaseCore):
    """Realize logic for money page."""

    __slots__ = ("db", "core")

    def prepare_insert_data(self, data: dict) -> None:
        if data["type"]:
            data.pop("hours")
        data["name"] = data["name"] or data["value"]
        data["type"] = "hour" if data["type"] else "shift"

    def add_rate(self, data: dict) -> RateRow:
        """Add new rate."""
        self.prepare_insert_data(data)
        self.db.rate.insert(data)
        return self.db.rate.get(**data)  # type: ignore

    def add_bonus(self, data: dict) -> BonusRow:
        """Add new bonus."""
        data["name"] = data["name"] or data["value"]
        self.db.bonus.insert(data)
        return self.db.bonus.get(**data)  # type: ignore

    def all_rate(self) -> list[RateRow]:
        """Getting rate."""
        return self.db.rate.select(state=1)

    def all_bonus(self) -> list[BonusRow]:
        """Getting rate."""
        return self.db.bonus.select(state=1)

    def update_item(self, data: dict, item) -> RateRow | BonusRow:
        """Update rate or bonus."""
        if data.get("type"):
            self.prepare_insert_data(data)

        for key, value in data.items():
            setattr(item, key, value)

        item.change()
        return item

    def delete_rate(self, id: int) -> None:
        """Delete curent rate, change state to 2 it is deleted status."""
        self.db.rate.update({"state": 2}, id=id)

    def delete_bonus(self, id: int) -> None:
        """Delete curent bonus, change state to 2 it is deleted status."""
        self.db.bonus.update({"state": 2}, id=id)


class WorkMaker(BaseCore):
    """Subcore for work maker view page."""

    __slots__ = ("db", "core")

    def get_rates(self) -> dict[str, RateRow]:
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
        bonuses: Iterable[BonusRow],
    ) -> None:
        """Save bonuses."""
        for bonus in bonuses:
            self.db.work_bonus.add({
                "work_id": work_id,
                "bonus_id": bonus.id,
            })

    def save_work(
        self,
        rate: RateRow,
        bonuses: Iterable[BonusRow],
        start_datetime: datetime,
        end_datetime: datetime,
        # start_dt: datetime,
        # start_tm: time,
        # end_dt: datetime,
        # end_tm: time,
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


class Main(BaseCore):
    """Subcore for main page."""

    __slots__ = ("db", "core", "work_maker", "months_name")

    def __init__(self, core, db) -> None:
        super().__init__(core, db)
        self.work_maker = WorkMaker(core, db)
        self.months_name = {
            "01": "Январь",
            "02": "Февраль",
            "03": "Март",
            "04": "Апрель",
            "05": "Май",
            "06": "Июнь",
            "07": "Июль",
            "08": "Август",
            "09": "Сентябрь",
            "10": "Октябрь",
            "11": "Ноябрь",
            "12": "Декабрь",
        }

    def _get_work_years(self) -> set[str]:
        """Get works year from start and end datetime."""
        stmt = "SELECT {} FROM Work".format(
            "DISTINCT substr(start_datetime, 1, 4)",
        )
        start_dttms = self.db.execute(
            stmt,
            result=ResultFetch.fetchall
        )
        stmt = "SELECT {} FROM Work".format(
            "DISTINCT substr(end_datetime, 1, 4)",
        )
        end_dttms = self.db.execute(
            stmt,
            result=ResultFetch.fetchall
        )

        return {
            i[0]
            for i in {*start_dttms, *end_dttms}  # type: ignore
        }

    def _get_work_month_by_year(self, year: str) -> set[str]:
        """Get works month from start and end datetime by year."""
        stmt = "SELECT {} FROM Work WHERE {}".format(
            "DISTINCT substr(start_datetime, 6, 2)",
            f"substr(start_datetime, 1, 4) = '{year}'"
        )
        starts_dttms = self.db.execute(
            stmt,
            result=ResultFetch.fetchall
        )

        stmt = "SELECT {} FROM Work WHERE {}".format(
            "DISTINCT substr(end_datetime, 6, 2)",
            f"substr(end_datetime, 1, 4) = '{year}'"
        )
        end_dttms = self.db.execute(
            stmt,
            result=ResultFetch.fetchall
        )

        return {
            i[0]
            for i in {*starts_dttms, *end_dttms}  # type: ignore
        }

    def filters_data(self, year: str) -> tuple[map, dict[str, str]]:
        """Get filters data month and years."""
        years = self._get_work_years()
        months = self._get_work_month_by_year(year)

        months_dict = {
            str(month): self.months_name[month]
            for month in sorted(months)
        }
        return map(lambda x: str(x), sorted(years)), months_dict

    def get_works(self, month: str, year: str) -> list["WorkRow"]:
        """Get works by year and month."""
        stmt = "{} == '{}' AND {} == '{}' OR {} == '{}' AND {} == '{}'"
        return self.db.work.select(
            condition=stmt.format(
                "substr(start_datetime, 1, 4)",
                year,
                "substr(start_datetime, 6, 2)",
                month,
                "substr(end_datetime, 1, 4)",
                year,
                "substr(end_datetime, 6, 2)",
                month,
            )
        )

    def fetch_value_by_works(self, work: "WorkRow") -> float:
        """Fetch money value by work."""
        value = 0
        rate = work.rate
        bonuses = work.bonuses

        if rate.type == "shift":
            value += rate.value

        for bonus in bonuses:
            value += bonus.value
        return value
