import itertools
import json
import logging
import pathlib
from typing import Annotated

import typer

from photosite_backend.backends import dest_type_options, get_fs
from photosite_backend.image import get_images, hash_file, hash_image, write_image
from photosite_backend.manifest import (
    Manifest,
    generate_manifest,
    generate_manifest_entry,
    write_manifest,
)

logging.basicConfig(level=logging.INFO)


app = typer.Typer()


@app.command()
def sync(
    source_path: Annotated[
        pathlib.Path, typer.Argument(help="Path to source directory")
    ],
    dest: Annotated[str, typer.Argument(help="Destination path or bucket name")],
    dest_type: dest_type_options = "dir",
):
    """
    Reads in the images in source_path. Generates a manifest. Writes the images
    and manifest to the selected dest, deleting any existing contents.
    """

    dest_fs = get_fs(dest, dest_type)
    image_paths = get_images(source_path)

    dest_fs = get_fs(dest, dest_type)

    existing_manifest: Manifest | None = None
    try:
        with dest_fs.open("manifest.json", "rb") as file:
            existing_manifest = json.load(file)
    except FileNotFoundError:
        pass

    for image_path in image_paths:
        image_hash = hash_image(image_path)

        # if the image already exists in the manifest, check it has a file hash
        # and if that matches the new file, skip uploading.
        if (
            existing_manifest
            and (entry := existing_manifest["images"].get(image_hash))
            and (existing_hash := entry.get("file_hash"))
        ):
            new_hash = hash_file(image_path)
            if new_hash == existing_hash:
                logging.info(
                    "Skipping upload of %s as it is already up to date in dest",
                    image_path,
                )
                continue

        write_image(dest_fs, image_path)

    new_manifest = generate_manifest(image_paths)

    existing_files = dest_fs.glob("*")
    expected_files = list(
        itertools.chain(
            "manifest.json",
            *[
                (entry["filename"], entry["thumbnail"])
                for entry in new_manifest["images"].values()
            ],
        )
    )
    unwanted_files = [file for file in existing_files if file not in expected_files]
    for file_path in unwanted_files:
        dest_fs.rm(file_path)

    if new_manifest != existing_manifest:
        write_manifest(dest_fs, new_manifest)


@app.command()
def hash(image_path: pathlib.Path):
    """
    Get the hash of a provided image file. This only takes into account the image
    bytes themselves, not metadata, so is stable when changing tags.
    """

    logging.info("Hash of `%s`: `%s`", image_path.name, hash_image(image_path))


@app.command()
def add(
    dest: Annotated[str, typer.Argument(help="Destination path or bucket name")],
    image_path: pathlib.Path,
    dest_type: dest_type_options = "dir",
):
    """
    Add a single image to dest.
    """

    image_hash = hash_image(image_path)
    file_hash = hash_file(image_path)

    dest_fs = get_fs(dest, dest_type)

    manifest: Manifest | None = None
    try:
        with dest_fs.open("manifest.json", "rb") as file:
            manifest = json.load(file)
    except FileNotFoundError:
        pass

    if manifest:
        # check whether the image already exists in the manifest and is up to
        # date with any changes.
        if (image_entry := manifest["images"].get(image_hash)) and image_entry.get(
            "file_hash"
        ) == file_hash:
            logging.info(
                "Skipping upload of %s as it is already up to date in dest",
                image_path,
            )
            return

        manifest["images"][image_hash] = generate_manifest_entry(image_path)
    else:
        manifest = generate_manifest([image_path])

    write_image(dest_fs, image_path)
    write_manifest(dest_fs, manifest)


@app.command()
def remove(
    dest: Annotated[str, typer.Argument(help="Destination path or bucket name")],
    hash: Annotated[str, typer.Argument(help="Image hash of image to remove")],
    dest_type: dest_type_options = "dir",
):
    """
    Remove an image by hash from the dest.
    """

    dest_fs = get_fs(dest, dest_type)

    with dest_fs.open("manifest.json", "rb") as file:
        manifest: Manifest = json.load(file)

    entry = manifest["images"].get(hash)
    if not entry:
        logging.error("Provided hash `%s` not found in the manifest!", hash)
        exit(1)

    try:
        dest_fs.rm(entry["filename"])
    except FileNotFoundError:
        pass

    try:
        dest_fs.rm(entry["thumbnail"])
    except (FileNotFoundError, KeyError):
        pass

    del manifest["images"][hash]

    write_manifest(dest_fs, manifest)


if __name__ == "__main__":
    app()
