__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

from ast import parse
import sys
import argparse
import inspire_info
from urllib.parse import quote
import os
import math
from inspire_info.InspireInfo import InspireInfo


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--name_proposal',
                        action='store_true',
                        help="Write out name_proposal.txt")
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)
    parser.add_argument('--use_custom_name_proposal',
                        type=str,
                        help="Names of the people to match",
                        default=None)
    parser.add_argument('--retrieve',
                        action='store_true',
                        help="""If added API-call is created, otherwise
            cache-file is going to be used.""")
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

    parsed_args = parser.parse_args(args)

    if parsed_args.lower_date == 'None':
        parsed_args.lower_date = None
    if parsed_args.upper_date == 'None':
        parsed_args.upper_date = None

    return dict(vars(parsed_args))


def main(arguments):
    parsed_args = parse_args(args=arguments)
    inspire_getter = InspireInfo(config_path=parsed_args["config"])

    if parsed_args["use_custom_name_proposal"] is not None:
        inspire_getter.name_proposal = parsed_args["use_custom_name_proposal"]

    print("Overwriting lower_date and upper_date in config with: {} {}".format(
        parsed_args["lower_date"], parsed_args["upper_date"]))

    inspire_getter.config["lower_date"] = parsed_args["lower_date"]
    inspire_getter.config["upper_date"] = parsed_args["upper_date"]
    inspire_getter.get_data()
    inspire_getter.read_name_proposal()
    inspire_getter.match_publications_by_authors()

    inspire_getter.print_clickable_links(match_type="matched")

if __name__ == "__main__":
    main(sys.argv[1:])
