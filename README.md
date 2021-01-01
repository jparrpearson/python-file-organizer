# python-file-organizer

Organizes files based on their modified date, or optionally the EXIF modified date for `JPG` images.  Files are copied or moved to a destination folder with a directory structure based on the modified date.

For example, a file with a modified date of `2020-12-30 00:01:02` would be moved to `$output/2020/12/filename.ext` (assuming a granularity of `month`).

## Prerequisites

Requires Python 3.6+ and pip to be installed:
```sh
$ python -V
$ pip -V
```

Also relies on the exif package:
```sh
$ pip install exif
```

## Usage

Get help:
```sh
$ python organizer.py --help
```

Organize a folder of images, using the EXIF modifed date:
```sh
$ python organizer.py --input "/C/Pictures/Unsorted" --output "/C/Pictures/Sorted" --exif
```

## License

Copyright (c) 2020 Jeremy Parr-Pearson

The MIT License (MIT)
