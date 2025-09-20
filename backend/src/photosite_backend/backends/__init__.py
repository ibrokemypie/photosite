from typing import Literal

from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.local import LocalFileSystem
from s3fs import S3FileSystem

import photosite_backend.backends.s3 as s3

dest_type_options = Literal["dir", "s3"]


def get_fs(dest: str, dest_type: dest_type_options):
    if dest_type == "dir":
        return DirFileSystem(dest, LocalFileSystem())
    if dest_type == "s3":
        account_id, access_key, access_key_secret, is_r2 = (
            s3.get_configuration_from_env()
        )

        extra_kwargs = {}
        if is_r2:
            extra_kwargs["client_kwargs"] = dict(
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                region_name="auto",
            )
            extra_kwargs["s3_additional_kwargs"] = dict(ACL="private")
        return DirFileSystem(
            dest,
            S3FileSystem(key=access_key, secret=access_key_secret, **extra_kwargs),
        )

    raise
