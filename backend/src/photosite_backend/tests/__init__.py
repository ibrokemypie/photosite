import pathlib
from importlib.resources import files

from photosite_backend.tests import test_data


def create_test_datafile(test_temp_dir: pathlib.Path, source_filename: str):
    """
    Creates a copy of a file from the test_data module in the provided pytest
    tmp_path directory.

    Returns the path to the new file.
    """

    source_path = files(test_data) / (source_filename)
    dest_path = test_temp_dir / source_filename

    dest_path.write_bytes(source_path.read_bytes())

    return dest_path
