import json
import logging
import pathlib
from typing import Annotated

import typer

from photosite_backend.backends import dest_type_options, get_fs
from photosite_backend.image import get_images, hash_image, write_image
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

    manifest = generate_manifest(image_paths)

    for image_path in image_paths:
        write_image(dest_fs, image_path)

    write_manifest(dest_fs, manifest)


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

    dest_fs = get_fs(dest, dest_type)

    write_image(dest_fs, image_path)

    manifest: Manifest | None = None

    try:
        with dest_fs.open("manifest.json", "rb") as file:
            manifest = json.load(file)

        manifest["images"][hash_image(image_path)] = generate_manifest_entry(image_path)
    except FileNotFoundError:
        pass

    if not manifest:
        manifest = generate_manifest([image_path])

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

    dest_fs.rm(entry["filename"])
    del manifest["images"][hash]

    write_manifest(dest_fs, manifest)


if __name__ == "__main__":
    app()
