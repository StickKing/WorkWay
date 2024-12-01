from typing import TYPE_CHECKING
from typing import Literal
from typing import TypedDict


if TYPE_CHECKING:
    from workway.core.db.tables import BonusRow


class TCompleteBonus(TypedDict):
    """Completed bonus dict for core."""

    bonus: "BonusRow"
    on_full_sum: bool


class TCompleteRework(TypedDict):
    """Completed bonus dict for core."""

    value: float
    type: Literal["%", "sum"]


class TCompleteOtherIncome(TypedDict):
    """Completed other income dict for core."""

    name: str
    value: float
