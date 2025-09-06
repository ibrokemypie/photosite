# Todo

## Make the manifest

- Have a function that saves a dict to a file in the outdir
- Set a manifest version const and key in the dict
- Add an 'images' key which is a dict of `hash.ext` to dicts of image metadata


## Write the output image files

- Make an in-memory copy of the image file to act on
- Strip out all metadata that doesn't match a whitelist
- Write this amended image file to `hash.ext` in outdir
- Make it possible to override specific metadata fields with constant values
