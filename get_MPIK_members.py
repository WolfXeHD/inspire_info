__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import sys
import requests
import json
import time
import argparse
from urllib.parse import quote
import inspire_info
import tqdm
import math
import datetime


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--institute',
                        type=str,
                        default="Heidelberg, Max Planck Inst.")
    parser.add_argument('--format',
                        type=str,
                        default="json",
                        choices=["json", "bibtex", "latex-eu", "latex-us"])
    parser.add_argument('--lower_date',
                        type=str,
                        default=None,
                        help="needs to be in format YYYY-MM-DD.")
    parser.add_argument('--upper_date',
                        type=str,
                        default=None,
                        help="needs to be in format YYYY-MM-DD.")
    parser.add_argument(
        '--retrieve',
        action='store_true',
        help=
        "If added API-call is created, otherwise cache-file is going to be used."
    )
    parser.add_argument(
        '--cache_file',
        type=str,
        required=True,
        help="cache file to store/read data, depending on --retrieve")

    parser.add_argument('--size',
                        type=int,
                        default=500,
                        help="size of queried package")
    parser.add_argument(
        '--get_links',
        action='store_true',
        help="Prints the inspire quieries to the found publications")

    return dict(vars(parser.parse_args()))


def main(arguments):
    parsed_args = parse_args(args=arguments)
    size = parsed_args["size"]

    # get the inspire id of the institute
    institute_and_time_query = inspire_info.build_query_template(
        lower_date=parsed_args["lower_date"],
        upper_date=parsed_args["upper_date"])

    global_query = institute_and_time_query.format(
        page='1', size=str(size), institute=quote(parsed_args["institute"]))

    keywords_to_check = [
        "neutrino",
        "bsm",
        "darkmatter",
        "dm",
        "double beta decay",
        "double chooz",
        "conus",
        "stereo",
        "xenon",
        "darwin",
        "borexino",
        "gerda",
        "legend",
        "neutrino: oscillation",
        "neutrino: mixing",
        "double-beta decay",
    ]

    if parsed_args["retrieve"]:
        # retrieving data
        data = inspire_info.read_from_inspire(formatted_query=global_query)
        total_hits = data["hits"]["total"]
        n_pages = int(total_hits / int(size)) + 1
        for i in tqdm.tqdm(range(n_pages)):
            if i > 0:
                time.sleep(0.5)
                this_query = institute_and_time_query.format(
                    page=str(i + 1),
                    size=str(size),
                    institute=quote(parsed_args["institute"]))
                temp_data = inspire_info.read_from_inspire(
                    formatted_query=this_query)
                data["hits"]["hits"] += temp_data["hits"]["hits"]

        with open(parsed_args["cache_file"], "w") as f:
            json.dump(data, f)
    else:
        print("Loading data...")
        with open(parsed_args["cache_file"], "r") as f:
            data = json.load(f)
        total_hits = data["hits"]["total"]

    matched_publications = []
    unmachted_publications = []

    weird_publications = []

    # filter by keywords
    publications_without_keywords = []
    for publication in data["hits"]["hits"]:
        pub = inspire_info.Publication(publication)
        if parsed_args["lower_date"]:
            datetime_object = datetime.datetime.strptime(
                parsed_args["lower_date"], "%Y-%m-%d")
            if pub.earliest_date_year < datetime_object.year:
                weird_publications.append(pub)
                continue

        if pub.keywords is not None:
            for keyword in keywords_to_check:
                if keyword in pub.keywords:
                    matched_publications.append(pub)
                    break
            else:
                unmachted_publications.append(pub)
        else:
            publications_without_keywords.append(pub)
            continue

    #  print(
    #      inspire_info.get_publication_query(weird_publications, clickable=True))

    all_authors_from_MPIK_named = inspire_info.get_matched_authors(
        publications=matched_publications,
        institute=parsed_args["institute"],
        people_to_exclude=["Blaum"])

    with open("name_proposal.txt", "w") as f:
        for name in sorted(all_authors_from_MPIK_named):
            f.write(name + "\n")

    if parsed_args["get_links"]:
        print(len(matched_publications))
        for i in range(math.ceil(len(matched_publications) / 100)):
            print(100 * i, 100 * (i + 1))
            print(len(matched_publications[100 * i:100 * (i + 1)]))

            clickalbe_link = inspire_info.get_publication_query(
                matched_publications[100 * i:100 * (i + 1)], clickable=True)
            print("LINK {i}".format(i=i))
            print(clickalbe_link)
            print()
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
