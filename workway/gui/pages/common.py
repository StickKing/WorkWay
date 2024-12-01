"""Module constains common controls."""
from typing import Any
from typing import MutableMapping

from flet import Alignment
from flet import BottomSheet
from flet import Column
from flet import Container
from flet import CrossAxisAlignment
from flet import MainAxisAlignment
from flet import Padding
from flet import Row
from flet import Text
from flet import TextStyle


class PresentatorSheet(BottomSheet):
    """Presentation item in botton sheet."""

    def __init__(
        self,
        item: Any,
        attr_names: MutableMapping[str, str],
    ) -> None:
        """Initialize."""
        contents = []
        style = TextStyle(18)
        for title, attr_name in attr_names.items():
            title_field = Text(
                f"{title}: ",
                style=style,
            )
            attr = getattr(item, attr_name)
            if isinstance(attr, bool):
                text_field = Text(
                    "Да" if attr else "Нет",
                    style=style,
                )
            else:
                text_field = Text(
                    attr,
                    style=style,
                )
            contents.append(
                Row([title_field, text_field])
            )

        super().__init__(
            Container(
                content=Column(
                    contents,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                padding=Padding(left=20, top=20, right=20, bottom=20),
                alignment=Alignment(0, 0),
            ),
        )
