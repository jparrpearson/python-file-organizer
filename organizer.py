#!/usr/bin/python

import os
import shutil
import time
from argparse import ArgumentParser
from argparse import BooleanOptionalAction
from datetime import datetime
from exif import Image

# TODO: Allow for include/exclude filters (globs)
# TODO: Allow for granularity to hour, minute, and second

parser = ArgumentParser()
parser.add_argument("-a", "--action", default="copy", choices=["copy", "move"], help="the action to perform on the files")
parser.add_argument("-e", "--exif", default=False, action=BooleanOptionalAction, help="use EXIF metadata for images")
parser.add_argument("-g", "--granularity", default="month", choices=["year", "month", "day"], help="granularity of output directories")
parser.add_argument("-i", "--input", default="./in", help="location of input files")
parser.add_argument("-o", "--output", default="./out", help="location to save output files")
args = parser.parse_args()

def scan_tree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry

def get_entry_date(entry):
    return datetime.fromtimestamp(entry.stat().st_mtime)

def get_exif_date(path):
    with open(entry.path, "rb") as image_file:
        image = Image(image_file)
        return datetime.strptime(image.datetime, "%Y:%m:%d %H:%M:%S")

for entry in scan_tree(f"{args.input}"):
    print(f"Found file {entry.path}")
    modified_date = (get_exif_date(entry.path) if args.exif and entry.path.lower().endswith(".jpg")
            else get_entry_date(entry))
    if args.granularity == "year":
        date_path = str(modified_date.year)
    elif args.granularity == "month":
        date_path = str(modified_date.year) + os.sep + str(modified_date.month).zfill(2)
    elif args.granularity == "day":
        date_path = str(modified_date.year) + os.sep + str(modified_date.month).zfill(2) + os.sep + str(modified_date.day).zfill(2)
    output_folder = args.output + os.sep + date_path
    output_file = output_folder + os.sep + entry.name

    print(f"Saving to {output_file}")
    os.makedirs(output_folder, exist_ok=True)
    if args.action == "copy":
        shutil.copy(entry.path, output_file)
    elif args.action == "move":
        shutil.move(entry.path, output_file)
