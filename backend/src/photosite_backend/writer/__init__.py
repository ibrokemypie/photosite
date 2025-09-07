import pathlib
import json


def write_manifest(output_dir: pathlib.Path, manifest_contents: dict):
    manifest_path = output_dir / "manifest.json"

    with manifest_path.open("w") as file:
        json.dump(manifest_contents, file)

    return manifest_path
