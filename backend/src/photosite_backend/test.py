from importlib.resources import files
from types import ModuleType
from typing import Literal


def open_test_datafile(
    data_module: ModuleType, path: str, mode: Literal["r"] | Literal["rb"] = "rb"
):
    return (files(data_module) / (path)).open(mode)
