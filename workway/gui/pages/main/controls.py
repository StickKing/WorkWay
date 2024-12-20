"""Module contain work presantator."""
from typing import TYPE_CHECKING

from flet import BottomSheet
from flet import Column
from flet import Container
from flet import ControlEvent
from flet import DataCell
from flet import DataColumn
from flet import DataRow
from flet import DataTable
from flet import ElevatedButton
from flet import ListTile
from flet import MainAxisAlignment
from flet import Padding
from flet import Row
from flet import ScrollMode
from flet import Text
from flet import TextStyle
from flet import TextThemeStyle
from flet import alignment
from flet import colors

from workway.core.subcores.work import Сalculation
from workway.gui.pages.common import AlertDialogInfo

from .views import UpdateWorkView


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
            DataColumn(Text("Название")),
            DataColumn(Text("Тип")),
            DataColumn(Text("Сумма в руб."), numeric=True),
        ]
        data_table_column = Column(
            [
                Container(
                    content=Column(
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Container(
                                Text(
                                    work.name,
                                    theme_style=TextThemeStyle.TITLE_LARGE,
                                ),
                                alignment=alignment.center,
                            ),
                            Container(
                                Text(
                                    "{} - {}".format(
                                        work.start_dttm.strftime(r"%d %B %Y %H:%M"),
                                        work.end_dttm.strftime(r"%d %B %Y %H:%M"),
                                    ),
                                    theme_style=TextThemeStyle.BODY_MEDIUM,
                                ),
                                alignment=alignment.center,
                            ),
                            Row(
                                [
                                    ElevatedButton(
                                        "Удалить",
                                        bgcolor=colors.ERROR_CONTAINER,
                                        color=colors.WHITE,
                                        on_click=lambda e: self.page.open(
                                            AlertDialogInfo(
                                                "Удаление выхода на работу",
                                                f"Удалить '{work.name[:20]}'?",
                                                "Да",
                                                self.delete_this,
                                                "Нет",
                                            )
                                        ),
                                    ),
                                    ElevatedButton(
                                        "Изменить",
                                        bgcolor="#ffc107",
                                        color="#343a40",
                                        on_click=self.update_this,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_AROUND,
                            ),
                        ],
                    )
                ),
                DataTable(
                    columns=columns,
                    rows=self._prepare_rows(),
                ),
            ],
            scroll=ScrollMode.HIDDEN,
            alignment=MainAxisAlignment.CENTER,
        )
        super().__init__(
            content=Container(
                content=data_table_column,
                padding=Padding(left=10, top=0, right=10, bottom=0),
                width=450,
                alignment=alignment.center,
            ),
            enable_drag=True,
            use_safe_area=True,
        )

    def _prepare_rows(self) -> list[DataRow]:
        """Prepare rows with data."""
        calculation = Сalculation.from_work(self.core, self.work)

        data_table_rate = calculation.rate_calc.fetch_data_table_view()
        rate = DataRow(
            cells=[
                DataCell(Text(data_table_rate["name"])),
                DataCell(Text(data_table_rate["type"])),
                DataCell(Text(data_table_rate["money"])),
            ]
        )

        data_table_bonuses = [
            DataRow(
                cells=[
                    DataCell(Text(bonus["name"])),
                    DataCell(Text(bonus["type"])),
                    DataCell(Text(bonus["money"])),
                ]
            )
            for bonus in calculation.bonus_calc.fetch_data_table_view()
        ]

        data_table_rework = calculation.rework_calc.fetch_data_table_view()
        if data_table_rework:
            rework_row = DataRow(
                cells=[
                    DataCell(Text(data_table_rework["name"])),
                    DataCell(Text(data_table_rework["type"])),
                    DataCell(Text(round(data_table_rework["money"], 2))),
                ]
            )
            data_table_bonuses.append(rework_row)

        other_income = [
            DataRow(
                cells=[
                    DataCell(Text(income["name"])),
                    DataCell(Text("Доп. доход")),
                    DataCell(
                        Text("{}".format(round(income["value"], 2))),
                    ),
                ]
            )
            for income in self.work.other_income
        ]

        work_money = DataRow(
            cells=[
                DataCell(Text("")),
                DataCell(Text("Итог")),
                DataCell(Text(f"{round(self.work.value, 2)}")),
            ]
        )
        return [
            rate,
            *data_table_bonuses,
            *other_income,
            work_money,
        ]

    def delete_this(self, event: ControlEvent) -> None:
        """Delete this control."""
        self.core.delete_work(self.work)
        self.page.views[-1].content.change_dropdowns(self)
        self.page.close(self)

    def update_this(self, event: ControlEvent) -> None:
        """Open view for update work."""
        self.page.close(self)
        self.page.views.append(
            UpdateWorkView(self.core.work_maker, self.work),
        )
        self.page.update()
