from pathlib import Path
from tempfile import TemporaryDirectory

import piexif
from PIL.ExifTags import Base

from photosite_backend.test import open_test_datafile

from . import ALLOWED_EXTENSIONS, get_files, hash_image, read_tags, test_data


class TestGetFiles:
    def test_get_files_empty_dir(self):
        with TemporaryDirectory() as dir:
            dir_path = Path(dir)
            assert get_files(dir_path) == set()

    def test_get_files_wrong_type(self):
        with TemporaryDirectory() as dir:
            dir_path = Path(dir)
            file = dir_path / "somefile.txt"
            file.touch()
            assert get_files(dir_path) == set()

    def test_get_files_correct_type(self):
        with TemporaryDirectory() as dir:
            dir_path = Path(dir)
            files = {dir_path / f"somefile{ext}" for ext in ALLOWED_EXTENSIONS}
            [file.touch() for file in files]
            assert get_files(dir_path) == files


class TestReadTags:
    def test_read_tags(self):
        with (
            TemporaryDirectory() as dir,
            open_test_datafile(test_data, "photo_1.jpg") as file,
        ):
            filepath = Path(dir) / "photo_1.jpg"
            filepath.write_bytes(file.read())

            tags = read_tags(filepath)

            assert tags == {
                Base.Make: "OLYMPUS CORPORATION",
                Base.Model: "E-M10MarkII",
                Base.DateTime: "2019:10:22 18:00:27",
            }


class TestHashImage:
    def test_hash_image(self):
        with (
            TemporaryDirectory() as dir,
            open_test_datafile(test_data, "photo_1.jpg") as file,
        ):
            filepath = Path(dir) / "photo_1.jpg"
            filepath.write_bytes(file.read())

            assert (
                hash_image(filepath)
                == "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24"
            )

    def test_hash_image_different_metadata(self):
        # here we show that hash_image will return the same value whether
        # the image has tags or not
        with (
            TemporaryDirectory() as dir,
            open_test_datafile(test_data, "photo_1.jpg") as file,
        ):
            orig = Path(dir) / "orig.jpg"
            orig.write_bytes(file.read())

            file.seek(0)

            cleaned = Path(dir) / "cleaned.jpg"
            piexif.remove(file.read(), cleaned)

            assert hash_image(cleaned) == hash_image(orig)
            assert read_tags(cleaned) == {}
            assert read_tags(orig) != {}

    def test_hashes_are_different(self):
        # sanity check that two different images have two different hashes
        with (
            TemporaryDirectory() as dir,
            open_test_datafile(test_data, "photo_1.jpg") as file_one,
            open_test_datafile(test_data, "photo_2.jpg") as file_two,
        ):
            path_one = Path(dir) / "photo_1.jpg"
            path_one.write_bytes(file_one.read())

            path_two = Path(dir) / "photo_2.jpg"
            path_two.write_bytes(file_two.read())

            assert hash_image(path_one) != hash_image(path_two)
