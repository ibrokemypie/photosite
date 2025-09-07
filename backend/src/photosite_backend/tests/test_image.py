from pathlib import Path

import piexif

from photosite_backend.image import (
    ALLOWED_EXTENSIONS,
    get_files,
    hash_image,
    read_tags,
)
from photosite_backend.tests import create_test_datafile


class TestGetFiles:
    def test_get_files_empty_dir(self, tmp_path: Path):
        assert get_files(tmp_path) == set()

    def test_get_files_wrong_type(self, tmp_path: Path):
        file = tmp_path / "somefile.txt"
        file.touch()
        assert get_files(tmp_path) == set()

    def test_get_files_correct_type(self, tmp_path: Path):
        files = {tmp_path / f"somefile{ext}" for ext in ALLOWED_EXTENSIONS}
        [file.touch() for file in files]
        assert get_files(tmp_path) == files


class TestReadTags:
    def test_read_tags(self, tmp_path: Path):
        with (
            create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file,
        ):
            filepath = tmp_path / "photo_1.jpg"
            filepath.write_bytes(file.read())

            tags = read_tags(filepath)

            assert tags == {
                "Make": "OLYMPUS CORPORATION",
                "Model": "E-M10MarkII",
                "DateTime": "2019:10:22 18:00:27",
            }


class TestHashImage:
    def test_hash_image(self, tmp_path: Path):
        with (
            create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file,
        ):
            filepath = tmp_path / "photo_1.jpg"
            filepath.write_bytes(file.read())

            assert (
                hash_image(filepath)
                == "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24"
            )

    def test_hash_image_different_metadata(self, tmp_path: Path):
        # here we show that hash_image will return the same value whether
        # the image has tags or not
        with (
            create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file,
        ):
            orig = tmp_path / "orig.jpg"
            orig.write_bytes(file.read())

            file.seek(0)

            cleaned = Path(tmp_path) / "cleaned.jpg"
            piexif.remove(file.read(), cleaned)

            assert hash_image(cleaned) == hash_image(orig)
            assert read_tags(cleaned) == {}
            assert read_tags(orig) != {}

    def test_hashes_are_different(self, tmp_path: Path):
        # sanity check that two different images have two different hashes
        with (
            create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file_one,
            create_test_datafile(tmp_path, "photo_2.jpg").open("rb") as file_two,
        ):
            path_one = tmp_path / "photo_1.jpg"
            path_one.write_bytes(file_one.read())

            path_two = tmp_path / "photo_2.jpg"
            path_two.write_bytes(file_two.read())

            assert hash_image(path_one) != hash_image(path_two)
