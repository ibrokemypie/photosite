import pathlib
from importlib.resources import files
from typing import Literal

from photosite_backend.tests import test_data


def get_datafile_path(tmp_path: pathlib.Path, path: str):
    base_dir = tmp_path

    return base_dir / path


def open_test_datafile(
    tmp_path: pathlib.Path, path: str, mode: Literal["r"] | Literal["rb"] = "rb"
):
    dest_path = get_datafile_path(tmp_path, path)
    source_path = files(test_data) / (path)

    dest_path.write_bytes(source_path.read_bytes())
    dest_path.seek(0)

    return dest_path.open(mode)
