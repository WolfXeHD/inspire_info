#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import glob
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Merge bibtex files into one file')
    parser.add_argument('--source_dir',
                        type=str,
                        help="Directory where the bibtex-output is stored.",
                        required=True
                        )
    parser.add_argument('--output_file',
                        type=str,
                        help="File to save the output.",
                        required=True
                        )

    return dict(vars(parser.parse_args()))


def main():
    parsed_args = parse_args()
    files_query = parsed_args["source_dir"] + "/*"
    files = glob.glob(files_query)

    total_data = ""
    for file in files:
        with open(file, "r") as f:
            data = f.read()
        total_data += "\n\n"
        total_data += data

    with open(parsed_args["output_file"], "w") as f:
        f.write(total_data)
    print("{} files merged into {}".format(
        len(files), parsed_args["output_file"]))
