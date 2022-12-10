#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.10'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import inspire_info
import json
import os
import tqdm
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Command line tool to search for authors in inspire')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        default=None
                        )
    parser.add_argument('--authors_output_dir',
                        type=str,
                        help="Directory to save the output.",
                        default="authors")

    return dict(vars(parser.parse_args()))


def main():
    parsed_args = parse_args()
    search_authors_and_download(**parsed_args)

if __name__ == "__main__":
    main()
