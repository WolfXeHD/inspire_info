__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import sys
import argparse
from urllib.parse import quote
import inspire_info
import math
import os
import tqdm


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument(
        '--retrieve',
        action='store_true',
        help="""If added API-call is created, otherwise 
            cache-file is going to be used."""
    )
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

    config = inspire_info.read_config(parsed_args["config"])
    size = config["size"]
    keywords_to_check = config["keywords"]
    lower_date = config["lower_date"]
    upper_date = config["upper_date"]
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

    if parsed_args["create_cache"] and not parsed_args["retrieve"]:
        raise Exception("Cache should be created only if API-call is made! Do you miss the --retrieve flag?")

    if parsed_args["create_cache"]:
        inspire_info.write_data(filename=cache_file, data=data)

    matched_publications = []
    unmatched_publications = []
    # weird_publications = []

    # filter by keywords
    publications_without_keywords = []
    for publication in tqdm.tqdm(data["hits"]["hits"]):
        pub = inspire_info.Publication(publication)
        # if lower_date:
        #     datetime_object = datetime.datetime.strptime(
        #         lower_date, "%Y-%m-%d")
        #     if pub.earliest_date_year < datetime_object.year:
        #         weird_publications.append(pub)
        #         continue

        if pub.keywords is not None:
            for keyword in keywords_to_check:
                if keyword in pub.keywords:
                    matched_publications.append(pub)
                    break
            else:
                unmatched_publications.append(pub)
        else:
            publications_without_keywords.append(pub)
            continue

    all_authors_from_institution_named = inspire_info.get_matched_authors(
        publications=matched_publications,
        institute=institute,
        people_to_exclude=config["people_to_exclude"])

    if parsed_args["get_name_proposal"]:
        print("Writing out", name_proposal)
        with open(name_proposal, "w") as f:
            for name in sorted(all_authors_from_institution_named):
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
