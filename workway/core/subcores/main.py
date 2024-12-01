"""Module contain main page subcore."""
from typing import TYPE_CHECKING

from lildb.enumcls import ResultFetch

from .base import BaseCore
from .work import WorkMaker


if TYPE_CHECKING:
    from ..db.tables import WorkRow


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

    def delete_work(self, work: "WorkRow") -> None:
        """Delete work from db."""
        self.db.work_bonus.delete(work_id=work.id)
        work.delete()
