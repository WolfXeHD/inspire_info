#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
import os
from datetime import datetime
from inspire_info.InspireInfo import InspireInfo


def parse_args():
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)
    parser.add_argument('--title_to_find',
                        type=str,
                        help="Title to find in the publications.",
                        required=True)
    return dict(vars(parser.parse_args()))


def main():
    parsed_args = parse_args()
    inspire_getter = InspireInfo(parsed_args["config"])
    inspire_getter.get_data()
    print("Finding publications with title:", parsed_args["title_to_find"])
    print()
    found = False
    for pub in inspire_getter.publications:
        if parsed_args["title_to_find"] in pub.title:
            print(pub, "ID:", pub.id)
            found = True

    if not found:
        print("No publications found with title:", parsed_args["title_to_find"])


if __name__ == "__main__":
    main()
