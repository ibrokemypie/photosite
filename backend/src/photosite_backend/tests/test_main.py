import pathlib

from photosite_backend.main import return_hi, write_output
from photosite_backend.tests import create_test_datafile


def test_return_hi():
    assert return_hi() == "hi!"


def test_write_output(
    tmp_path: pathlib.Path,
):
    # test that inputs get read and written to output dir with manifest and
    # a set of the written file paths is returned

    input_path = tmp_path / "input"
    input_path.mkdir()

    output_path = tmp_path / "output"
    output_path.mkdir()

    create_test_datafile(input_path, "photo_1.jpg")
    create_test_datafile(input_path, "photo_2.jpg")

    written_files = write_output(input_path, output_path)
    output_files = set(output_path.glob("*"))

    assert written_files == output_files

    assert set(output_file.name for output_file in output_files) == {
        "manifest.json",
        "c6e9ec51b31e15299990d475ac83e70ebde470f5a66e6ddfb0fce341caaff6ea.jpg",
        "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg",
    }
