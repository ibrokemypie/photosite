from pathlib import Path

from photosite_backend.image import (
    ALLOWED_EXTENSIONS,
    PERMANENT_TAGS,
    get_exiftool,
    get_images,
    hash_image,
    read_tags,
    write_image,
)
from photosite_backend.tests import create_test_datafile


class TestGetImages:
    def test_get_images_empty_dir(self, tmp_path: Path):
        assert get_images(tmp_path) == set()

    def test_get_images_wrong_type(self, tmp_path: Path):
        file = tmp_path / "somefile.txt"
        file.touch()
        assert get_images(tmp_path) == set()

    def test_get_images_correct_type(self, tmp_path: Path):
        images = {tmp_path / f"somefile{ext}" for ext in ALLOWED_EXTENSIONS}
        [file.touch() for file in images]
        assert get_images(tmp_path) == images


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
            cleaned.write_bytes(file.read())
            get_exiftool().clear(cleaned)

            assert hash_image(cleaned) == hash_image(orig)

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


def test_clear_exif_tags(tmp_path):
    with (
        create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file,
    ):
        orig = tmp_path / "orig.jpg"
        orig.write_bytes(file.read())

        file.seek(0)

        cleaned = tmp_path / "cleaned.jpg"
        cleaned.write_bytes(file.read())
        get_exiftool().clear(cleaned)

        assert set(read_tags(orig).keys()) != PERMANENT_TAGS
        assert set(read_tags(cleaned).keys()).issubset(PERMANENT_TAGS)


def test_set_exif_tags(tmp_path):
    with (
        create_test_datafile(tmp_path, "photo_1.jpg").open("rb") as file,
    ):
        cleaned = tmp_path / "cleaned.jpg"
        cleaned.write_bytes(file.read())
        new_tags = {
            "IPTC:Caption-Abstract": "OLYMPUS DIGITAL CAMERA",
        }
        et = get_exiftool()
        et.clear(cleaned)
        et.set_tags(cleaned, new_tags)

        assert set(read_tags(cleaned).keys()) == PERMANENT_TAGS | new_tags.keys()


def test_write_image(tmp_path: Path):
    image_path = create_test_datafile(tmp_path, "photo_1.jpg")

    output_dir = tmp_path

    output_path = write_image(output_dir, image_path)
    assert (
        output_path.name
        == "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg"
    )
    assert image_path.read_bytes() == output_path.read_bytes()
