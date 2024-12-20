"""Module constains common controls."""
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import MutableMapping

from flet import AlertDialog
from flet import Alignment
from flet import BottomSheet
from flet import Column
from flet import Container
from flet import CrossAxisAlignment
from flet import MainAxisAlignment
from flet import Padding
from flet import Row
from flet import Text
from flet import TextButton
from flet import TextStyle


if TYPE_CHECKING:
    from flet import ControlEvent


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
                    attr[:20],
                    style=style,
                )
            contents.append(
                Row([title_field, text_field])
            )

        info_column = Column(
            contents,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        super().__init__(
            Container(
                content=info_column,
                padding=Padding(left=20, top=20, right=20, bottom=20),
                alignment=Alignment(0, 0),
                width=450,
            ),
            enable_drag=True,
            use_safe_area=True,
        )


class AlertDialogInfo(AlertDialog):
    """Alert dialog for information about other."""

    def __init__(
        self,
        title: str,
        body: str,
        button1_text: str | None = None,
        button1_func: Callable | None = None,
        button2_text: str | None = "Закрыть",
        button2_func: Callable | None = None,
    ) -> None:
        """Initialize"""
        if button2_text == "Закрыть" or button2_text == "Нет":
            button2_func = self.close_dialog

        button1_func = self.wrap_button1_func(button1_func)

        buttons = {
            button1_text: button1_func,
            button2_text: button2_func,
        }
        super().__init__(
            title=Text(title),
            content=Text(body),
            actions=[
                TextButton(text, on_click=func)
                for text, func in buttons.items()
                if func
            ]
        )

    def wrap_button1_func(
        self,
        func: Callable | None,
    ) -> Callable[["ControlEvent"], None] | None:
        """Run button 1 func and close modal."""
        if func is None:
            return None
        def func_with_close_dialog(event: "ControlEvent") -> None:
            func(event)
            self.close_dialog(event)
        return func_with_close_dialog

    def close_dialog(self, event: "ControlEvent") -> None:
        """Close this dialog."""
        self.page.close(self)
