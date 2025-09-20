import hashlib
import logging
from pathlib import Path
from typing import Any, List

import exiftool
from exiftool import ExifToolHelper
from fsspec.implementations.dirfs import DirFileSystem
from PIL import Image

from photosite_backend.utils import cache, lru_cache

ALLOWED_EXTENSIONS = (".jpg", ".jpeg")

# these are the keys left behind by exiftool after removing ALL
# 'tags'
PERMANENT_TAGS = {
    "Composite:ImageSize",
    "Composite:Megapixels",
    "ExifTool:ExifToolVersion",
    "File:BitsPerSample",
    "File:ColorComponents",
    "File:CurrentIPTCDigest",
    "File:Directory",
    "File:EncodingProcess",
    "File:FileAccessDate",
    "File:FileInodeChangeDate",
    "File:FileModifyDate",
    "File:FileName",
    "File:FilePermissions",
    "File:FileSize",
    "File:FileType",
    "File:FileTypeExtension",
    "File:ImageHeight",
    "File:ImageWidth",
    "File:MIMEType",
    "File:YCbCrSubSampling",
    "SourceFile",
    "IPTC:ApplicationRecordVersion",
}


def get_images(input_path: Path):
    return {
        entry
        for entry in input_path.iterdir()
        if (entry.is_file() and entry.suffix in ALLOWED_EXTENSIONS)
    }


@lru_cache(maxsize=5)
def hash_image(image_path: Path):
    # hashes just the image data, not the metadata, for identifying images
    # even when their metadata has been modified.

    with Image.open(image_path) as img:
        image_bytes = img.tobytes()
        sha256_hash = hashlib.sha256(image_bytes).hexdigest()
        return sha256_hash


class ExifToolWithClear(ExifToolHelper):
    def clear(self, files: Any | List[Any]):
        """
                    Delete all tags for the given files.

                :param files: File(s) to be worked on.

            * If a non-iterable is provided, it will get tags for a single item (str(non-iterable))
            * If an iterable is provided, the list is passed into :py:meth:`execute_json` verbatim.

            .. note::
                Any files/params which are not bytes/str will be casted to a str in :py:meth:`execute()`.

            .. warning::
                Currently, filenames are NOT checked for existence!  That is left up to the caller.

            .. warning::
                Wildcard strings are valid and passed verbatim to exiftool.

                However, exiftool's wildcard matching/globbing may be different than Python's matching/globbing,
                which may cause unexpected behavior if you're using one and comparing the result to the other.
                Read `ExifTool Common Mistakes - Over-use of Wildcards in File Names`_ for some related info.

        :type files: Any or List(Any) - see Note

        :return: The format of the return value is the same as for :py:meth:`exiftool.ExifTool.execute_json()`.


                :raises ValueError: Invalid Parameter
                :raises TypeError: Invalid Parameter
                :raises ExifToolExecuteError: If :py:attr:`check_execute` == True, and exit status was non-zero

                .. _ExifTool Common Mistakes - Over-use of Wildcards in File Names: https://exiftool.org/mistakes.html#M2

        """

        final_files: List = self.__class__._parse_arg_files(files)
        exec_params: List = []

        exec_params.extend(["-all="])
        exec_params.extend(final_files)
        try:
            ret = self.execute(*exec_params)
        except exiftool.exceptions.ExifToolOutputEmptyError:
            raise
            # raise RuntimeError(f"{self.__class__.__name__}.get_tags: exiftool returned no data")
        except exiftool.exceptions.ExifToolJSONInvalidError:
            raise
        except exiftool.exceptions.ExifToolExecuteError:
            # if last_status is <> 0, raise an error that one or more files failed?
            raise

        return ret


# for now, just keep one instance of exiftool open for the duration of the
# tool's run time
@cache
def get_exiftool():
    et = ExifToolWithClear()
    et.common_args = (et.common_args or []) + ["-overwrite_original"]

    return et


@lru_cache(maxsize=5)
def read_tags(image_path: Path):
    exiftool = get_exiftool()
    # this library really seems to want to be run in bulk, todo: consider refactor
    # to use in bulk.
    tags: dict[str, Any] = exiftool.get_metadata(str(image_path))[0]
    return tags


def write_image(dest_fs: DirFileSystem, image_path: Path):
    """
    Writes an image into dest, named after its image hash.
    """

    output_filename = f"{hash_image(image_path)}{image_path.suffix}"
    dest_fs.write_bytes(output_filename, image_path.read_bytes())
    logging.info(
        "Wrote image `%s` to `%s/%s`",
        image_path.name,
        dest_fs.path,
        output_filename,
    )
