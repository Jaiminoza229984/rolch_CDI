# ruff: noqa: E402

from importlib.metadata import version
from importlib.util import find_spec

HAS_PANDAS = False
HAS_POLARS = False

if find_spec("pandas") is not None:
    HAS_PANDAS = True

if find_spec("polars") is not None:
    HAS_POLARS = True

from .information_criteria import InformationCriterion
from .scaler import OnlineScaler

__version__ = version("ondil")

__all__ = [
    "OnlineScaler",
    "InformationCriterion",
]
