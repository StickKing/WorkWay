"""Module constain setting page."""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

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
from flet import Icons

from .common import AlertDialogInfo
from .common import ContainerWithBorder


if TYPE_CHECKING:
    from flet import ControlEvent

    from workway.core.subcores import Settings


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
                        icon=Icons.UPLOAD_FILE,
                        text="Загрузить базу",
                        on_click=lambda e: self.file_picker_upload.pick_files(
                            "Выберите архив с базой",
                            allowed_extensions=["zip"],
                        ),
                    ),
                    ElevatedButton(
                        icon=Icons.SAVE,
                        text="Выгрузить в файл",
                        on_click=lambda e: self.file_picker_save.get_directory_path(
                            "Укажите куда сохранить work_db.zip",
                            # self.db_zip_name,
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

    @property
    def file_picker_save(self) -> "FilePicker":
        """Create file picker and return it."""
        self.page.update()
        return self.page.overlay[0]

    @property
    def file_picker_upload(self) -> "FilePicker":
        """Create file picker and return it."""
        self.page.update()
        return self.page.overlay[1]

    def get_archive_name(self, path: Path) -> str:
        """Check file name in yser path and create archive name."""
        archive_name = "work_way_db"
        index = 0
        for file in path.iterdir():
            if re.match(r"work_way_db[0-9]+\.zip", file.name):
                index_new = re.findall(r"[0-9]+", file.name)
                index_new = int(index_new[0]) + 1
                if index_new > index:
                    index = index_new
            if re.match(r"work_way_db\.zip", file.name) and index == 0:
                index = 1
        if index:
            return f"{archive_name}{index}"
        return archive_name

    def create_db_zip(self, event: "FilePickerResultEvent") -> None:
        """Create db zip archive."""
        if event.path is None:
            return
        save_path: Path = self.core.db.normalize_path(Path(event.path))

        try:
            archive_path = shutil.make_archive(
                self.get_archive_name(save_path),
                "zip",
                self.core.db_path.parent,
            )
            archive_path = self.core.db.normalize_path(Path(archive_path))
            shutil.move(archive_path, str(save_path))
        except Exception:
            self.page.open(AlertDialogInfo("Ошибка", "Что-то пошло не так"))

    def upload_db_zip(self, event: "FilePickerResultEvent") -> None:
        """Upload data base."""
        if not event.files:
            return
        db_path = self.core.db.normalize_path(self.core.db_path)
        db_path.unlink()
        try:
            shutil.unpack_archive(event.files[0].path, str(db_path.parent))
        except Exception:
            self.page.open(AlertDialogInfo("Ошибка", "Что-то пошло не так"))

        self.core.reinitialize_db()

    def build(self) -> None:
        if self.page.overlay:
            return
        self.page.overlay.append(
            FilePicker(
                on_result=self.create_db_zip,
            )
        )
        self.page.overlay.append(
            FilePicker(
                on_result=self.upload_db_zip,
            )
        )
        # self.page.update()
