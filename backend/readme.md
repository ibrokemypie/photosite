# Requirements

Python >=3.11
exiftool

# Todo


## Write the output image files

It turns out EXIF isn't the only image metadata format, theres also IPTC,
photoshop and others. And the data seems to be copied across all the formats for
a given file. I think instead of a whitelist, its going to make more sense to
have a blacklist and a rewrite list.

- Add regex rewrite list for tags
- Add whitelist for tags written into manifest
- Make the lists all configurable through CLI
- Add config file based on CLI options
