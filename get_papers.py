__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import sys
import argparse
import inspire_info
from urllib.parse import quote
import os
import math


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
    parser.add_argument(
        '--retrieve',
        action='store_true',
        help="""If added API-call is created, otherwise 
            cache-file is going to be used."""
    )
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
    if parsed_args["use_custom_name_proposal"] is None:
        name_proposal = parsed_args['config'].replace(".yaml",
                                                      "_name_proposal.txt")
    else:
        name_proposal = parsed_args["use_custom_name_proposal"]
    with open(name_proposal, "r") as f:
        names = f.read().splitlines()

    config = inspire_info.read_config(parsed_args["config"])

    size = config["size"]

    lower_date = parsed_args["lower_date"]
    upper_date = parsed_args["upper_date"]
    print("Overwriting lower_date and upper_date in config with: {} {}".format(
        lower_date, upper_date))

    config["lower_date"] = lower_date
    config["upper_date"] = upper_date

    institute = config["institute"]
    config_path = os.path.abspath(parsed_args["config"])
    cache_file = config_path.replace(".yaml", ".pkl")
    config["cache_file"] = cache_file
    name_proposal = config_path.replace(".yaml", "_name_proposal.txt")

    # get the inspire id of the institute
    institute_and_time_query = inspire_info.build_query_template(
        lower_date=lower_date, upper_date=upper_date)

    global_query = institute_and_time_query.format(page='1',
                                                   size=str(size),
                                                   institute=quote(institute))
    print(global_query)

    data = inspire_info.get_data(
        global_query=global_query,
        retrieve=parsed_args["retrieve"],
        institute_and_time_query=institute_and_time_query,
        config=config)

    matched_publications = []
    unmatched_publications = []
    for publication in data["hits"]["hits"]:
        pub = inspire_info.Publication(publication)
        matched = False
        for author_to_check in names:
            if author_to_check in pub.author_names:
                idx = pub.author_names.index(
                    author_to_check)
                candidate_author = pub.author_objects[idx]
                if candidate_author.affiliations is not None:
                    for affiliation in candidate_author.affiliations:
                        if affiliation == institute:
                            matched_publications.append(pub)
                            matched = True
                            break
            if matched:
                break
        if not matched:
            unmatched_publications.append(pub)

    for i in range(math.ceil(len(matched_publications) / 100)):
        print(100 * i, 100 * (i + 1))
        print(len(matched_publications[100 * i:100 * (i + 1)]))

        clickalbe_link = inspire_info.get_publication_query(
            matched_publications[100 * i:100 * (i + 1)], clickable=True)
        print("LINK {i}".format(i=i))
        print(clickalbe_link)
        print()
        print()

    # inspire_info.get_tarball_of_publications(matched_publications, link_type="bibtex", target_dir="publications_bibtex")


    # print("Unmatched publications")
    # print(unmatched_publications)
    # clickalbe_link = inspire_info.get_publication_query(
    #     matched_publications, clickable=True)
    # print(clickalbe_link)


if __name__ == "__main__":
    main(sys.argv[1:])
