#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

from inspire_info.InspireInfo import InspireInfo
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Command line tool to search for authors in inspire')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True
                        )

    return dict(vars(parser.parse_args()))


def main():
    parsed_args = parse_args()
    inspire_getter = InspireInfo(parsed_args["config"])
    inspire_getter.search_authors_and_download()


if __name__ == "__main__":
    main()
