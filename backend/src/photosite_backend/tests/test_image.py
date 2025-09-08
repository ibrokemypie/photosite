from pathlib import Path

import piexif
import pytest

from photosite_backend.image import (
    ALLOWED_EXTENSIONS,
    find_tag_by_name,
    get_images,
    get_tag_value,
    hash_image,
    read_exif,
    write_image,
)
from photosite_backend.tests import create_test_datafile


@pytest.mark.parametrize(
    "tag_name, ifd_name, tag_id",
    [
        ("DateTimeOriginal", "Exif", 36867),
        ("DateTime", "0th", 306),
        ("Make", "0th", 271),
        ("Gamma", "Exif", 42240),
        ("GPSLatitude", "GPS", 2),
    ],
)
def test_find_tag_by_name(tag_name, ifd_name, tag_id):
    assert find_tag_by_name(tag_name) == (ifd_name, tag_id)


def test_cant_find_tag_by_name():
    with pytest.raises(ValueError, match="No tag with name `foobar` exists"):
        find_tag_by_name("foobar")


@pytest.mark.parametrize(
    "tag_name, tag_value",
    [
        ("Model", "E-M10MarkII"),
        ("DateTimeOriginal", "2017:01:06 11:05:48"),
        ("ShutterSpeedValue", (5906891, 1000000)),
        ("ExifVersion", "0231"),
    ],
)
def test_get_tag_value(tmp_path: Path, tag_name, tag_value):
    image_path = create_test_datafile(tmp_path, "photo_1.jpg")
    assert get_tag_value(image_path, tag_name) == tag_value


def test_get_tag_value_bad(tmp_path: Path):
    tag_name = "Model"
    expected_value = "E-M10MarkII"

    image_path = create_test_datafile(tmp_path, "photo_1.jpg")
    assert get_tag_value(image_path, tag_name) == expected_value


class TestGetFiles:
    def test_get_files_empty_dir(self, tmp_path: Path):
        assert get_images(tmp_path) == set()

    def test_get_files_wrong_type(self, tmp_path: Path):
        file = tmp_path / "somefile.txt"
        file.touch()
        assert get_images(tmp_path) == set()

    def test_get_files_correct_type(self, tmp_path: Path):
        files = {tmp_path / f"somefile{ext}" for ext in ALLOWED_EXTENSIONS}
        [file.touch() for file in files]
        assert get_images(tmp_path) == files


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

            cleaned = tmp_path / "cleaned.jpg"
            piexif.remove(file.read(), cleaned)

            empty_exif = {
                "0th": {},
                "1st": {},
                "Exif": {},
                "GPS": {},
                "Interop": {},
                "thumbnail": None,
            }

            assert hash_image(cleaned) == hash_image(orig)
            assert read_exif(cleaned) == empty_exif
            assert read_exif(orig) != empty_exif

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


def test_write_image(tmp_path: Path):
    image_path = create_test_datafile(tmp_path, "photo_1.jpg")

    output_dir = tmp_path

    output_path = write_image(output_dir, image_path)
    assert (
        output_path.name
        == "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg"
    )

    exif_data = read_exif(output_path)
    assert exif_data == {
        "0th": {
            271: b"OLYMPUS CORPORATION",
            272: b"E-M10MarkII",
            # this is "ExifTag" and seems to get left behind by piexif always
            34665: 82,
        },
        "1st": {},
        "Exif": {
            36867: b"2017:01:06 11:05:48",
        },
        "GPS": {},
        "Interop": {},
        "thumbnail": None,
    }
