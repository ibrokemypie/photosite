import hashlib
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Container, Literal, cast

import piexif
from PIL import Image

ALLOWED_EXTENSIONS = (".jpg", ".jpeg")

TAG_WHITELIST = {
    "Make",
    "Model",
    "DateTimeOriginal",
}


def get_images(input_path: Path):
    return {
        entry
        for entry in input_path.iterdir()
        if (entry.is_file() and entry.suffix in ALLOWED_EXTENSIONS)
    }


@lru_cache(5)
def hash_image(image_path: Path):
    # hashes just the image data, not the metadata, for identifying images
    # even when their metadata has been modified.

    with Image.open(image_path) as img:
        image_bytes = img.tobytes()
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        return sha256_hash


TagName = str
TagType = int
TagID = int
IFDName = str
IFDContents = dict[TagID, dict[Literal["name"] | Literal["type"], TagName | TagType]]
IFDDict = dict[IFDName, IFDContents]

ExifValues = dict[IFDName, dict[TagID, Any] | None]


@lru_cache(5)
def read_exif(image_path: Path):
    exif = piexif.load(str(image_path))
    return cast(ExifValues, exif)


def find_tag_by_name(tag_name: str):
    """
    Return the IFD name and Tag ID for given tag_name.

    May raise ValueError if the provided tag_name is invalid.
    """

    for ifd_name, ifd_tags in piexif.TAGS.items():
        for tag_id, tag_data in ifd_tags.items():
            if tag_data["name"] == tag_name:
                if ifd_name == "Image":
                    ifd_name = "0th"
                return ifd_name, tag_id

    raise ValueError(f"No tag with name `{tag_name}` exists")


def get_tag_value(image_path: Path, tag_name: str) -> str | None:
    """
    Takes an image path and a tag name. Searches for the tag name across
    all EXIF ifds and returns the first result's value if any.
    Casts value to string.

    May raise ValueError if the provided tag_name is invalid.
    """

    ifd_name, tag_id = find_tag_by_name(tag_name)
    exif_dict = read_exif(image_path)

    ifd_tags = exif_dict.get(ifd_name)
    if ifd_tags and tag_id in ifd_tags:
        value = ifd_tags[tag_id]
        if isinstance(value, bytes):
            value = value.decode()
        return value


def filter_tags(image_path: Path, tag_whitelist: Container[str]):
    """
    Filter out all EXIF tags of the provided file whose names do not match
    the provided whitelist.

    Returns the filtered EXIF dict.
    """

    exif_dict = read_exif(image_path)

    new_exif = {}

    for ifd_name, ifd_value in exif_dict.items():
        if ifd_value is None:
            new_exif[ifd_name] = None
            continue

        new_exif[ifd_name] = {}

        for tag_id, tag_value in ifd_value.items():
            tag_name = piexif.TAGS[ifd_name][tag_id]["name"]
            if tag_name in tag_whitelist:
                new_exif[ifd_name][tag_id] = tag_value

    return new_exif


def get_tags_flat(
    image_path,
):
    """
    Returns a flat map of filtered image tags with their values.
    """

    return {tag_name: get_tag_value(image_path, tag_name) for tag_name in TAG_WHITELIST}


def write_image(output_dir: Path, image_path: Path):
    """
    Writes an input image to the correct location in the output path based on
    its hash, with the exif data cleaned.

    todo: tag rewriting
    todo: configurable whielist
    """

    output_filename = f"{hash_image(image_path)}{image_path.suffix}"
    output_path = output_dir / output_filename

    new_tags = filter_tags(image_path, TAG_WHITELIST)

    with NamedTemporaryFile() as tempfile:
        piexif.remove(str(image_path), tempfile.name)
        piexif.insert(piexif.dump(new_tags), tempfile.name, str(output_path))

    return output_path
