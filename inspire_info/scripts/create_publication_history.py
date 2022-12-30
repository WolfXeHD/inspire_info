#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
import os
from datetime import datetime
from inspire_info.InspireInfo import InspireInfo
from inspire_info.LatexCreator import LatexCreator
from inspire_info.scripts.create_latex_doc import template as latex_template


def parse_args():
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)
    parser.add_argument('--update_authors',
                        action="store_true",
                        help="Update authors in the authors_output_dir.")
    parser.add_argument('--retrieve_data',
                        action="store_true",
                        help="Executes the download of the cache-file.")
    parser.add_argument('--year',
                        type=int,
                        help="Year to be used for the latex file.",
                        default=None)
    parser.add_argument(
        '--lower_date',
        type=str,
        help="String to execute further specifications on the database",
        default=None)
    parser.add_argument(
        '--upper_date',
        type=str,
        help="String to execute further specifications on the database",
        default=None)
    parser.add_argument("--target_html",
                        type=str,
                        help="Target html-file where the converted HTML should be copied to.",
                        default=None)
    parser.add_argument("--target_html_body",
                        type=str,
                        help="""Target html-file where the converted HTML (body only)
should be copied to.""",
                        default=None)
    parser.add_argument("--refresh",
                        action="store_true",
                        help="""Refresh the publications-folder.""")

    return dict(vars(parser.parse_args()))


def main():
    parsed_args = parse_args()
    inspire_getter = InspireInfo(parsed_args["config"])
    pandoc_command = inspire_getter.config.get("pandoc_command", "pandoc")

    if not inspire_getter.cache_exists or parsed_args["retrieve_data"]:
        inspire_getter.get_data(retrieve=True)
        inspire_getter.write_data()
    print(f"Data retrieved: {inspire_getter.has_data}")

    if parsed_args["update_authors"]:
        inspire_getter.search_authors_and_download()
    else:
        inspire_getter.download_missing_authors()

    lower_date = inspire_getter.config["lower_date"]
    upper_date = inspire_getter.config["upper_date"]

    if parsed_args["lower_date"] is not None:
        print("Overwriting lower_date in config with: {}".format(
            parsed_args["lower_date"]))
        lower_date = parsed_args["lower_date"]
    if parsed_args["upper_date"] is not None:
        print("Overwriting upper_date in config with: {}".format(
            parsed_args["upper_date"]))
        upper_date = parsed_args["upper_date"]

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

    # make list of years between two dates
    years = [lower_date.year +
             i for i in range(upper_date.year - lower_date.year + 2)]
    if parsed_args["lower_date"] is not None or parsed_args["upper_date"] is not None:
        years = [lower_date.year, upper_date.year]
    if parsed_args["year"] is not None:
        years = [parsed_args["year"], parsed_args["year"] + 1]

    for lower_year, upper_year in zip(years, years[1:]):
        lower_date = '{lower_year}-01-01'.format(lower_year=lower_year)
        upper_date = '{upper_year}-01-01'.format(upper_year=upper_year)

        abs_config_path = os.path.abspath(parsed_args["config"])
        abs_dir_config_path = os.path.dirname(abs_config_path)
        target_dir = os.path.join(abs_dir_config_path,
                                  "..",
                                  "publications_{lower_year}_{upper_year}".format(
                                      lower_year=lower_year, upper_year=upper_year))
        dict_to_parse = {"lower_date": lower_date,
                         "upper_date": upper_date,
                         "download": "bibtex",
                         "target_dir": target_dir,
                         "refresh": parsed_args["refresh"],
                         }
        inspire_getter.get_papers(**dict_to_parse)

        filename = "publications_{lower_year}_{upper_year}.tex".format(
            lower_year=lower_year, upper_year=upper_year)
        document_maker = LatexCreator(
            template=latex_template,
            source_folder=target_dir,
            bibtex_list=inspire_getter.downloaded_bibtex_files,
            filename=filename,
            conversion_style_to_html=inspire_getter.conversion_style_to_html,
            pandoc_command=pandoc_command
        )
        document_maker.make_bibliography()
        document_maker.create_latex_doc()
        document_maker.convert_latex_to_html()
        document_maker.write_html_body_to_file()
        if parsed_args["target_html"] is not None:
            document_maker.copy_html_to_target(target=parsed_args["target_html"])
        if parsed_args["target_html_body"] is not None:
            document_maker.copy_html_to_target(target=parsed_args["target_html_body"])


if __name__ == "__main__":
    main()
