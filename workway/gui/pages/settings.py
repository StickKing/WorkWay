"""Module constain setting page."""
from __future__ import annotations

import shutil
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Sequence

from flet import BorderRadius
from flet import Column
from flet import Container
from flet import ElevatedButton
from flet import FilePicker
from flet import FilePickerResultEvent
from flet import Margin
from flet import Padding
from flet import Radio
from flet import RadioGroup
from flet import Row
from flet import Switch
from flet import Text
from flet import TextThemeStyle
from flet import ThemeMode
from flet import colors
from flet import icons


if TYPE_CHECKING:
    from flet import ControlEvent

    from workway.core.subcores import Settings


class ContainerWithBorder(Container):
    """Container with color border and bg color."""

    def __init__(self, controls: Sequence) -> None:
        """Initialize."""
        super().__init__(
            content=Column(controls),
            margin=Margin(0, 0, 0, 10),
            padding=Padding(left=15, top=10, right=0, bottom=10),
            bgcolor=colors.SURFACE_VARIANT,
            border_radius=BorderRadius(
                top_left=12,
                top_right=12,
                bottom_left=12,
                bottom_right=12,
            ),
        )

    def build(self) -> None:
        """Change width by page width."""
        self.width = self.page.width  # type: ignore


class SettingPage(Container):
    """Setting page."""

    def __init__(self, core: "Settings") -> None:
        """Initialize."""
        self.core = core

        self.db_zip_name = "work_way_db"

        self.theme_radio_group = RadioGroup(
            content=Row([
                Radio(value="light", label="Светлая"),
                Radio(value="dark", label="Тёмная"),
            ]),  # type: ignore
            on_change=self.change_app_theme,
            value=core.current_theme,
        )

        super().__init__(
            content=Column([
                Container(
                    content=Text(
                        "Настройки",
                        theme_style=TextThemeStyle.TITLE_LARGE,
                    ),
                    margin=Margin(0, 0, 0, 30),
                ),
                ContainerWithBorder([
                    Text(
                        "Смена темы",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    self.theme_radio_group,
                ]),
                ContainerWithBorder([
                    Text(
                        "Импорт / Экспорт базы данных",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    ElevatedButton(
                        icon=icons.UPLOAD_FILE,
                        text="Загрузить базу",
                        on_click=lambda e: self.file_picker_upload.pick_files(
                            "Выберите архив с базой",
                            allowed_extensions=["zip"],
                        ),
                    ),
                    ElevatedButton(
                        icon=icons.SAVE,
                        text="Выгрузить в файл",
                        on_click=lambda e: self.file_picker_save.save_file(
                            "Сохранить базу данных",
                            self.db_zip_name,
                        ),
                    ),
                ]),
            ]),
            padding=Padding(left=15, top=10, right=15, bottom=10),
        )

    def change_app_theme(self, event: "ControlEvent") -> None:
        """Change app theme."""
        control: Switch = event.control
        match control.value:
            case "dark":
                self.page.theme_mode = ThemeMode.DARK
                self.core.set_theme("dark")
            case _:
                self.page.theme_mode = ThemeMode.LIGHT
                self.core.set_theme("light")
        self.page.update()

    @cached_property
    def file_picker_save(self) -> "FilePicker":
        """Create file picker and return it."""
        file_picker = FilePicker(
            on_result=self.create_db_zip,
        )
        self.page.overlay.append(file_picker)
        self.page.update()
        return file_picker

    @cached_property
    def file_picker_upload(self) -> "FilePicker":
        """Create file picker and return it."""
        file_picker = FilePicker(
            on_result=self.upload_db_zip,
        )
        self.page.overlay.append(file_picker)
        self.page.update()
        return file_picker

    def create_db_zip(self, event: "FilePickerResultEvent") -> None:
        """Create db zip archive."""
        save_path: Path = self.core.db.normalize_path(Path(event.path))

        if save_path.is_dir():
            archive_path = shutil.make_archive(
                self.db_zip_name,
                "zip",
                self.core.db_path.parent,
            )
            shutil.move(archive_path, str(save_path))
            return

        archive_path = shutil.make_archive(
            save_path.name,
            "zip",
            self.core.db_path.parent,
        )
        shutil.move(archive_path, str(save_path.parent))

    def upload_db_zip(self, event: "FilePickerResultEvent") -> None:
        """Upload data base."""
        if not event.files:
            return
        db_path = self.core.db.normalize_path(self.core.db_path)
        db_path.unlink()
        shutil.unpack_archive(event.files[0].path, str(db_path.parent))
        self.core.reinitialize_db()
