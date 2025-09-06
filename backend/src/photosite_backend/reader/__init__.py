"""
This file will contain the functions that read the image files' metadata for
writing into the manifest.
"""

import hashlib
import pathlib
from functools import lru_cache

from piexif import TAGS, ImageIFD, load
from PIL import Image

ALLOWED_EXTENSIONS = (".jpg", ".jpeg")


def get_files(directory_path: pathlib.Path):
    return {
        entry
        for entry in directory_path.iterdir()
        if (entry.is_file() and entry.suffix in ALLOWED_EXTENSIONS)
    }


def get_tag_name(tag_no):
    return TAGS["Image"][tag_no]["name"]


def read_tags(file_path: pathlib.Path):
    IMPORTANT_TAGS = (ImageIFD.Make, ImageIFD.Model, ImageIFD.DateTime)

    exif = load(str(file_path))["0th"]

    return {
        get_tag_name(tag_no): tag_val.decode()
        for tag_no, tag_val in exif.items()
        if tag_no in IMPORTANT_TAGS
    }


@lru_cache
def hash_image(image_path: pathlib.Path):
    # hashes just the image data, not the metadata, for identifying images
    # even when their metadata has been modified.

    with Image.open(image_path) as img:
        image_bytes = img.tobytes()
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        return sha256_hash
