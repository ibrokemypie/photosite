"""
This file will contain the functions that read the image files' metadata for
writing into the manifest.
"""

import hashlib
import pathlib

from PIL import ExifTags, Image

ALLOWED_EXTENSIONS = (".jpg", ".jpeg")


def get_files(directory_path: pathlib.Path):
    return {
        entry
        for entry in directory_path.iterdir()
        if (entry.is_file() and entry.suffix in ALLOWED_EXTENSIONS)
    }


def read_tags(file_path: pathlib.Path):
    IMPORTANT_TAGS = (
        ExifTags.Base.Make,
        ExifTags.Base.Model,
        ExifTags.Base.DateTime,
    )

    with Image.open(file_path) as im:
        exif = im.getexif()

        return {tag: exif[tag] for tag in IMPORTANT_TAGS if tag in exif}


def hash_image(image_path: pathlib.Path):
    # hashes just the image data, not the metadata, for identifying images
    # even when their metadata has been modified.

    with Image.open(image_path) as img:
        image_bytes = img.tobytes()
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        return sha256_hash
