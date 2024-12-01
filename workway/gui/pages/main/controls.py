"""Module contain work presantator."""
from typing import TYPE_CHECKING

from flet import BottomSheet
from flet import Column
from flet import ControlEvent
from flet import DataCell
from flet import DataColumn
from flet import DataRow
from flet import DataTable
from flet import ElevatedButton
from flet import ListTile
from flet import Text
from flet import TextStyle
from flet import colors


if TYPE_CHECKING:
    from workway.core.db.tables import WorkRow
    from workway.core.subcores import Main


class WorkTile(ListTile):
    """Work tile."""

    def __init__(self, core: "Main", work: "WorkRow") -> None:
        self.core = core
        self.work = work

        dt: str | None = None
        if work.start_dttm.date() == work.end_dttm.date():
            dt = work.start_dttm.strftime(r"%d.%m.%y")
        else:
            dt = "{}-{}".format(
                work.start_dttm.strftime(r"%d.%m.%y"),
                work.end_dttm.strftime(r"%d.%m.%y"),
            )
        style = TextStyle(
            size=16,
        )

        super().__init__(
            leading=Text(
                work.name[:15],
                style=TextStyle(size=15),
                width=100,
            ),
            title=Text(dt, style=TextStyle(size=14)),
            trailing=Text(f"+{work.pretify_money}", style=style),
            on_click=lambda e: self.page.open(
                WorkInfoSheet(core, work),
            )
        )


class WorkInfoSheet(BottomSheet):
    """Work info about calculation."""

    def __init__(self, core: "Main", work: "WorkRow") -> None:
        self.core = core
        self.work = work
        columns = [
            DataColumn(Text("Наименование")),
            DataColumn(Text("Тип")),
            DataColumn(Text("Сумма в руб."), numeric=True),
        ]
        super().__init__(
            content=DataTable(
                columns=columns,
                rows=self._prepare_rows(),
            ),
        )

    def _prepare_rows(self) -> list[DataRow]:
        """Prepare rows with data."""
        rate = DataRow(
            cells=[
                DataCell(Text(self.work.rate.name)),
                DataCell(Text("ставка")),
                DataCell(Text(str(self.work.rate.value))),
            ]
        )

        sum_bonus = [
            DataRow(
                cells=[
                    DataCell(Text(bonus.name)),
                    DataCell(Text("бонус")),
                    DataCell(Text(str(bonus.value))),
                ]
            )
            for bonus in self.work.bonuses
            if bonus.type == "fix"
        ]

        work_money = DataRow(
            cells=[
                DataCell(Text("")),
                DataCell(Text("")),
                DataCell(Text(f"Итог: {self.work.value}")),
            ]
        )
        buttons = DataRow(
            cells=[
                DataCell(Text("")),
                DataCell(Text("")),
                DataCell(
                    ElevatedButton(
                        "Удалить",
                        bgcolor=colors.ERROR_CONTAINER,
                        color=colors.WHITE,
                        on_click=self.delete_this,
                    ),
                ),
            ]
        )
        return [rate, *sum_bonus, work_money, buttons]

    def delete_this(self, event: ControlEvent) -> None:
        """Delete this control."""
        self.core.delete_work(self.work)
        self.page.views[-1].content.change_dropdowns(self)
        self.page.close(self)


class WorkPresentator:
    """Presantation work."""

    def __init__(self, core: "Main") -> None:
        self.core = core

    def get_base(self, month: str, year: str):
        return Column([
            WorkTile(work)
            for work in self.core.get_works(month, year)
        ])
