#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.4'
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
    parser.add_argument('--search_name',
                        type=str,
                        help="Name to search for.",
                        default=None
                        )
    parser.add_argument('--custom_name_proposal',
                        type=str,
                        help="Names of the people to search for.",
                        default=None)
    parser.add_argument('--authors_output_dir',
                        type=str,
                        help="Directory to save the output.",
                        default="authors")

    return dict(vars(parser.parse_args()))

def main():
    parsed_args = parse_args()
    if parsed_args['search_name'] is None and parsed_args['custom_name_proposal'] is None:
        raise ValueError("Please provide a search name or a custom name proposal.")

    if parsed_args["custom_name_proposal"] is not None:
        with open(parsed_args["custom_name_proposal"], "r", encoding='unicode-escape') as f:
            authors = [line.strip() for line in f]
    else:
        authors = [parsed_args["search_name"]]

    print("Saving authors to directory: {}".format(parsed_args["authors_output_dir"]))
    if not os.path.exists(parsed_args["authors_output_dir"]):
        os.makedirs(parsed_args["authors_output_dir"])

    print("Searching for authors")
    for author in tqdm.tqdm(authors):
        query = inspire_info.myutils.build_person_query(author, size=5)
        data = inspire_info.myutils.read_from_inspire(query, silent=True)
        path_to_save = os.path.join(parsed_args["authors_output_dir"], f"author_{author}.txt")
        with open(path_to_save, "w") as f:
            json.dump(data, f)

if __name__ == "__main__":
    main()
