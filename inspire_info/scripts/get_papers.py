#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
import glob
import os

import inspire_info
from inspire_info.InspireInfo import InspireInfo


def parse_args():
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)
    parser.add_argument(
        '--lower_date',
        type=str,
        help="String to execute further specifications on the database",
        required=True)
    parser.add_argument(
        '--upper_date',
        type=str,
        help="String to execute further specifications on the database",
        required=True)

    parser.add_argument('--authors_output_dir',
                        type=str,
                        help="Directory to save the output.",
                        default="authors")

    parser.add_argument('--download',
                        type=str,
                        help="Type of file to be downloaded from inspire",
                        choices=[
                            'bibtex', 'latex-eu', 'latex-us', 'json', 'cv',
                            'citations', 'None'
                        ],
                        default="None")

    parser.add_argument("--target_dir",
                        type=str,
                        help="Directory to save the output.",
                        default=None)

    parsed_args = parser.parse_args()

    if parsed_args.lower_date == 'None':
        parsed_args.lower_date = None
    if parsed_args.upper_date == 'None':
        parsed_args.upper_date = None

    return dict(vars(parsed_args))


def get_papers(config, lower_date, upper_date, authors_output_dir, download, target_dir):
    inspire_getter = InspireInfo(config_path=config)

    print("Overwriting lower_date and upper_date in config with: {} {}".format(
        lower_date, upper_date))

    inspire_getter.config["lower_date"] = lower_date
    inspire_getter.config["upper_date"] = upper_date
    inspire_getter.get_data()

    #  filelist_query = os.path.join(authors_output_dir, "*.txt")
    filelist = []
    for author in inspire_getter.authors:
        author_file = os.path.join(authors_output_dir, f"author_{author}.txt")
        filelist.append(author_file)
    print("Found {} files in {}".format(len(filelist), authors_output_dir))

    bais_to_check = inspire_info.myutils.get_inspire_bais_from_filelist(
        filelist)
    inspire_getter.match_publications_by_authors(bais_to_check)
    collaborations_to_check = ["XENON", "GERDA"]
    inspire_getter.match_publications_by_collaborations(
        collaborations_to_check)
    inspire_getter.print_clickable_links(match_type="matched")

    missing_publications = inspire_getter.check_missing_publications_on_disk(
        inspire_getter.matched_publications, link_type=download, target_dir=target_dir)

    if download != "None":
        inspire_getter.download_publications(
            publications=missing_publications,
            link_type=download,
            target_dir=target_dir
        )


def main():
    parsed_args = parse_args()
    get_papers(**parsed_args)


if __name__ == "__main__":
    main()
