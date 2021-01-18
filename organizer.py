#!/usr/bin/python

import os
import shutil
import time
from argparse import ArgumentParser
from argparse import BooleanOptionalAction
from datetime import datetime
from exif import Image

# TODO: Process files in multiple threads
# TODO: Allow for include/exclude filters (globs)

parser = ArgumentParser()
parser.add_argument("-a", "--action", default="copy", choices=["copy", "move"], help="the action to perform on the files")
parser.add_argument("-d", "--debug", default=False, action=BooleanOptionalAction, help="whether to print debug messages")
parser.add_argument("-e", "--exif", default=True, action=BooleanOptionalAction, help="use EXIF metadata for images")
parser.add_argument("-g", "--granularity", default="month", choices=["year", "month", "day", "hour", "minute", "second"], help="granularity of output directories; pattern overrides")
parser.add_argument("-i", "--input", default="./in", help="location of input files")
parser.add_argument("-o", "--output", default="./out", help="location to save output files")
parser.add_argument("-p", "--pattern", help="output folder pattern, overrides granularity; pattern can include '{year}', '{month}', '{day}', '{hour}', '{minute}', '{second}', or '{sep}' (separator character)")
args = parser.parse_args()

def scan_tree(path):
    """
    Scan all files in a directory recursively.
    """
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry

def get_entry_date(entry):
    """
    Get the last modified date from the file metadata.
    """
    return datetime.fromtimestamp(entry.stat().st_mtime)

def get_exif_date(path):
    """
    Get the last modified date from the EXIF metadata, otherwise returns an empty string.
    """
    with open(entry.path, "rb") as image_file:
        image = Image(image_file)
        # image.has_exif still returns true if the EXIF metadata is empty, leading to an error, so catch that condition
        try:
            return datetime.strptime(image.datetime, "%Y:%m:%d %H:%M:%S")
        except:
            return ""

def get_date_path(granularity, date):
    """
    Create a path string from the date base on the granularity.  Returns an empty string if the granularity is not supported.
    e.g.: granularity="day", date="2020-03-27 14:00:04" returns "2020/03/27"
    """
    if granularity == "second":
        return get_date_path("minute", date) + os.sep + str(date.second).zfill(2)
    elif granularity == "minute":
        return get_date_path("hour", date) + os.sep + str(date.minute).zfill(2)
    elif granularity == "hour":
        return get_date_path("day", date) + os.sep + str(date.hour).zfill(2)
    elif granularity == "day":
        return get_date_path("month", date) + os.sep + str(date.day).zfill(2)
    elif granularity == "month":
        return get_date_path("year", date) + os.sep + str(date.month).zfill(2)
    elif granularity == "year":
        return str(date.year)
    else:
        return ""

def get_pattern_path(pattern, date):
    """
    Create a path string from the date based on a custom pattern.
    e.g.: patten="{year}{sep}{year}-{month}", date="2020-03-27 14:00:04" returns "2020/2020-03"
    """
    pattern = pattern.replace("{year}", str(date.year))
    pattern = pattern.replace("{month}", str(date.month).zfill(2))
    pattern = pattern.replace("{day}", str(date.day).zfill(2))
    pattern = pattern.replace("{hour}", str(date.hour).zfill(2))
    pattern = pattern.replace("{minute}", str(date.minute).zfill(2))
    pattern = pattern.replace("{second}", str(date.second).zfill(2))
    pattern = pattern.replace("{sep}", os.sep)
    return pattern

count = 0
for entry in scan_tree(f"{args.input}"):
    if args.debug:
        print(f"Found file {entry.path}")
    # Use EXIF datetime for JPG files, otherwise use file date (also fallback to file metadata for unreadable EXIF metadata)
    if args.exif and (entry.path.lower().endswith(".jpg") or entry.path.lower().endswith(".jpeg")):
        modified_date = get_exif_date(entry.path)
    if modified_date == "":
        modified_date = get_entry_date(entry)
    # Use pattern if provided, otherwise use the provided or default granularity for the output folder
    if args.pattern is not None:
        date_path = get_pattern_path(args.pattern, modified_date)
    else:
        date_path = get_date_path(args.granularity, modified_date)
    output_folder = args.output + os.sep + date_path
    output_file = output_folder + os.sep + entry.name

    if args.debug:
        print(f"Saving to {output_file}")
    os.makedirs(output_folder, exist_ok=True)
    if args.action == "copy":
        shutil.copy2(entry.path, output_file)
    elif args.action == "move":
        shutil.move(entry.path, output_file)
    count += 1

print(f"Processed {count} files")
