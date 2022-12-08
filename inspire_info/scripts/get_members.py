__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.2'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

from tkinter import W
from inspire_info.InspireInfo import InspireInfo
import sys
import argparse


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--retrieve',
                        action='store_true',
                        help="""If added API-call is created, otherwise 
            cache-file is going to be used.""")
    parser.add_argument(
        '--get_links',
        action='store_true',
        help="Prints the inspire quieries to the found publications")
    parser.add_argument('--get_name_proposal',
                        action='store_true',
                        help="Write out name_proposal.txt")
    parser.add_argument('--create_cache',
                        action='store_true',
                        help="Create the cache-file")
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)

    return dict(vars(parser.parse_args(args)))


def main(arguments):
    parsed_args = parse_args(args=arguments)

    inspire_getter = InspireInfo(config_path=parsed_args["config"])
    inspire_getter.get_data(retrieve=parsed_args["retrieve"])
    _, matched_publications, _ = inspire_getter.match_publications_by_keywords(
    )
    all_authors_from_institution_named = inspire_getter.match_authors(
        matched_publications)
    inspire_getter.name_proposal_data = all_authors_from_institution_named
    inspire_getter.write_name_proposal()

    if parsed_args["get_links"]:
        inspire_getter.print_links(match_type="matched")


if __name__ == "__main__":
    main(sys.argv[1:])
