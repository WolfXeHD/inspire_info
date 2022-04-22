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

    return dict(vars(parser.parse_args(args)))


def main(arguments):
    parsed_args = parse_args(args=arguments)
    if parsed_args["use_custom_name_proposal"] is None:
        name_proposal = parsed_args['config'].replace(".yaml",
                                                      "_name_proposal.txt")
    else:
        name_proposal = parsed_args["use_custom_name_proposal"]

    config = inspire_info.read_config(parsed_args["config"])
    with open(name_proposal, "r") as f:
        names = f.read().splitlines()

    config = inspire_info.read_config(parsed_args["config"])
    size = config["size"]
    keywords_to_check = config["keywords"]
    lower_date = config["lower_date"]
    upper_date = config["upper_date"]
    institute = config["institute"]
    config_path = os.path.abspath(parsed_args["config"])
    cache_file = config_path.replace(".yaml", ".json")
    config["cache_file"] = cache_file
    name_proposal = config_path.replace(".yaml", "_name_proposal.txt")

    with open(name_proposal, "r") as f:
        names = f.read().splitlines()

    # get the inspire id of the institute
    institute_and_time_query = inspire_info.build_query_template(
        lower_date=lower_date, upper_date=upper_date)

    global_query = institute_and_time_query.format(page='1',
                                                   size=str(size),
                                                   institute=quote(institute))

    data = inspire_info.get_data(
        global_query=global_query,
        retrieve=False,
        institute_and_time_query=institute_and_time_query,
        config=config)


    matched_publications = []
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

    #  #  non_matched_keywords = []
    #  for pub in matched_publications:
    #      pub.keywords
    #      #  if len(pub.author_names) > 2000:
    #      #      __import__('ipdb').set_trace()
    #      #  if pub.keywords is not None:
    #      #      intersection_set = list(set.intersection(set(pub.keywords), set(keywords_to_check)))
    #      #      if len(intersection_set) == 0:
    #      #          non_matched_keywords += pub.keywords
    #  #

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
