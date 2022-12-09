#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.9'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
from datetime import datetime
from inspire_info.InspireInfo import InspireInfo
from inspire_info.scripts.create_latex_doc import template as latex_template
from inspire_info.scripts.create_latex_doc import create_latex_doc
from inspire_info.scripts.search_authors_and_download import search_authors_and_download
from inspire_info.scripts.get_papers import get_papers

def parse_args():
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)
    parser.add_argument('--authors_output_dir',
                        type=str,
                        help="Directory to save the output.",
                        default="authors")
    parser.add_argument('--update_authors',
                        action="store_true",
                        help="Update authors in the authors_output_dir.")
    parser.add_argument('--retrieve_data',
                        action="store_true",
                        help="Executes the download of the cache-file.")
    parser.add_argument('--custom_name_proposal',
                        type=str,
                        help="Custom name proposal for the file to be used.",
                        default=None)
    parser.add_argument('--year',
                        type=int,
                        help="Year to be used for the latex file.",
                        default=None)

    return dict(vars(parser.parse_args()))

def main():
    parsed_args = parse_args()
    inspire_getter = InspireInfo(parsed_args["config"])
    if parsed_args["retrieve_data"]:
        inspire_getter.get_data(retrieve=True)
        inspire_getter.write_data()

    if inspire_getter.cache_exists:
        inspire_getter.get_data(retrieve=False)
    else:
        inspire_getter.get_data(retrieve=True)
        inspire_getter.write_data()
    print(f"Data retrieved: {inspire_getter.has_data}")


    if parsed_args["update_authors"]:
        dict_to_parse = {"custom_name_proposal": parsed_args["custom_name_proposal"],
                            "authors_output_dir": parsed_args["authors_output_dir"],
                            "search_name": None
        }
        search_authors_and_download(**dict_to_parse)

    lower_date = inspire_getter.config["lower_date"]
    upper_date = inspire_getter.config["upper_date"]

    # parse a string to a date object
    if lower_date is not None:
        lower_date = datetime.strptime(lower_date, "%Y-%m-%d")
    else:
        # set a default value
        lower_date = datetime.strptime("2006-01-01", "%Y-%m-%d")
    if upper_date is not None:
        upper_date = datetime.strptime(upper_date, "%Y-%m-%d")
    else:
        # set a default value
        upper_date = datetime.now()
    print(f"Lower date: {lower_date}, upper date: {upper_date}")

    #make list of years between two dates
    years = [lower_date.year + i for i in range(upper_date.year - lower_date.year + 2)]
    if parsed_args["year"] is not None:
        years = [parsed_args["year"], parsed_args["year"] + 1]

    l_bibtex_folders = []
    for lower_year, upper_year in zip(years, years[1:]):
        lower_date = '{lower_year}-01-01'.format(lower_year=lower_year)
        upper_date = '{upper_year}-01-01'.format(upper_year=upper_year)


        target_dir = "publications_{lower_year}".format(lower_year=lower_year)
        dict_to_parse = {"config": parsed_args["config"],
                        "lower_date": lower_date,
                        "upper_date": upper_date,
                        "authors_output_dir": parsed_args["authors_output_dir"],
                        "download": "bibtex",
                        "target_dir": target_dir}
        l_bibtex_folders.append(target_dir)
        get_papers(**dict_to_parse)

        out_dir = "latex_{target_dir}".format(target_dir=target_dir)
        create_latex_doc(latex_template, out_dir, target_dir, filename=f"publications_{lower_year}.tex")

if __name__ == "__main__":
    main()
