"""Base components."""
from abc import ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core import Core
    from ..db import DataBase


class BaseCore(ABC):
    """Page cls with all logic."""

    __slots__ = ("db", "core")

    def __init__(self, core: "Core", db: "DataBase") -> None:
        """Initialize."""
        self.db = db
        self.core = core
