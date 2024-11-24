"""Module contain work presantator."""
from typing import TYPE_CHECKING

from flet import Column
from flet import Container
from flet import ListTile
from flet import MainAxisAlignment
from flet import Margin
from flet import Row
from flet import Text
from flet import TextStyle


if TYPE_CHECKING:
    from workway.core.db.tables import WorkRow
    from workway.core.subcores import Main


class WorkTile(Container):
    """Work tile."""

    def __init__(self, work: "WorkRow") -> None:
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
            content=Row(
                [
                    Container(
                        Text(work.name[:15], style=style),
                        width=100,
                    ),
                    Container(
                        Text(dt, style=TextStyle(size=14)),
                        width=150,
                    ),
                    Container(Text(f"+{work.value} руб.", style=style)),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            margin=Margin(left=20, top=0, right=20, bottom=0),
        )
        # super().__init__(
        #     #leading=Text(work.name.rjust(15)),
        #     #title=Text(dt),
        #     title=Row([
        #         Text(work.name.ljust(15)),
        #         Text(dt),
        #     ]),
        #     trailing=Text(f"+{work.value}"),
        #     leading_and_trailing_text_style=style,
        # )


class WorkPresentator:
    """Presantation work."""

    def __init__(self, core: "Main") -> None:
        self.core = core

    def get_base(self, month: str, year: str):
        return Column([
            WorkTile(work)
            for work in self.core.get_works(month, year)
        ])
