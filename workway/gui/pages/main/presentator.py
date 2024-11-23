"""Module contain work presantator."""
from typing import TYPE_CHECKING

from flet import Column
from flet import ListTile
from flet import Text


if TYPE_CHECKING:
    from workway.core.db.tables import WorkRow
    from workway.core.subcores import Main


class WorkTile(ListTile):
    """Work tile."""

    def __init__(self, work: "WorkRow") -> None:
        self.work = work

        dt: str | None = None
        if work.start_datetime.date() == work.end_datetime.date():
            dt = work.start_datetime.strftime(r"%d.%m.%y")
        else:
            dt = "{}-{}".format(
                work.start_datetime.strftime(r"%d.%m.%y"),
                work.end_datetime.strftime(r"%d.%m.%y"),
            )
        super().__init__(
            leading=Text(work.name),
            title=Text(dt),
            trailing=Text("hello"),
        )


class WorkPresentator:
    """Presantation work."""

    core: Main

    def __init__(self, core) -> None:
        self.core = core

    def get_base(self):
        return Column([
            WorkTile(work)
            for work in self.core.get_works()
        ])
