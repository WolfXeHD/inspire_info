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
import myutils
import tqdm
import math


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
        "If true API-call is created, otherwise cache-file is going to be used."
    )
    parser.add_argument('--cache_file',
                        type=str,
                        required=True,
                        help="cache file to store data")

    parser.add_argument('--size',
                        type=int,
                        default=500,
                        help="size of queried package")

    return dict(vars(parser.parse_args()))


def main(arguments):
    parsed_args = parse_args(args=arguments)
    size = parsed_args["size"]

    # building query command
    institute_query = 'https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=aff:{institute}'
    time_query = myutils.build_time_query(lower_date=parsed_args["lower_date"],
                                          upper_date=parsed_args["upper_date"])
    if time_query != "":
        total_query = institute_query + " and " + time_query
    else:
        total_query = institute_query

    total_query = total_query.replace(" ", "%20")
    total_query = total_query.replace("\n", "")
    formatted_query = total_query.format(page='1',
                                         size=str(size),
                                         institute=quote(
                                             parsed_args["institute"]))

    keywords_to_check = [
        "neutrino", "bsm", "darkmatter", "dm", "double beta decay", "double chooz", "conus",
        "stereo", "xenon", "darwin", "borexino", "gerda", "legend", "neutrino: oscillation", "neutrino: mixing",
        "double-beta decay",
    ]

    if parsed_args["retrieve"]:
        # retrieving data
        data = myutils.read_from_inspire(formatted_query=formatted_query)
        total_hits = data["hits"]["total"]
        n_pages = int(total_hits / int(size)) + 1
        for i in tqdm.tqdm(range(n_pages)):
            if i > 0:
                time.sleep(0.5)
                this_query = total_query.format(page=str(i + 1),
                                                size=str(size),
                                                institute=quote(
                                                    parsed_args["institute"]))
                temp_data = myutils.read_from_inspire(
                    formatted_query=this_query)
                data["hits"]["hits"] += temp_data["hits"]["hits"]

        with open(parsed_args["cache_file"], "w") as f:
            json.dump(data, f)
    else:
        with open(parsed_args["cache_file"], "r") as f:
            data = json.load(f)
        total_hits = data["hits"]["total"]

    matched_publications = []
    unmachted_publications = []

    # filter by keywords
    publications_without_keywords = []
    for publication in data["hits"]["hits"]:
        meta = publication["metadata"]
        try:
            keywords = [item["value"].lower() for item in meta["keywords"]]
        except:
            publications_without_keywords.append(publications_without_keywords)
            continue
        publication["mykeywords"] = keywords

        for key in keywords_to_check:
            if key in keywords:
                matched_publications.append(publication)
                break
        else:
            unmachted_publications.append(publication)

    all_authors_from_MPIK = []
    for pub in matched_publications:
        for author in pub["metadata"]["authors"]:
            if "affiliations" in author.keys():
                affiliations = [affiliation["value"] for affiliation in author["affiliations"]]
            elif "raw_affiliations" in author.keys():
                affiliations = [affiliation["value"] for affiliation in author["raw_affiliations"]]
            else:
                affiliations = ["None"]

            if parsed_args["institute"] in affiliations:
                if "Blaum" in author["full_name"]:
                    continue
                all_authors_from_MPIK.append(author)
            #  else:
            #      for affiliation in affiliations:
            #          if "Kern" in affiliation:
            #              print("Suspect...")
            #              __import__('ipdb').set_trace()

    all_authors_from_MPIK_named = list(set([author["full_name"] for author in all_authors_from_MPIK]))
    with open("name_proposal.txt", "w") as f:
        for name in sorted(all_authors_from_MPIK_named):
            f.write(name + "\n")


        #  all_authors += [item["full_name"] for item in pub["metadata"]["authors"]]
    #  id_list = []
    #  for pub in matched_publications:
    #      id_list.append(pub["id"])

    #  matched_query = myutils.get_publication_by_id(id_list=id_list[:100], size=size)
    #  clickalbe_link = matched_query.replace("api/", "").replace("fields=titles,authors,id", "")
    #  matched_query = myutils.get_publication_query(matched_publications[:100], clickable=False)

    print(len(matched_publications))
    for i in range(math.ceil(len(matched_publications) / 100)):
        print(100 * i, 100 * (i + 1))
        print(len(matched_publications[100 * i: 100 * (i + 1)]))

        clickalbe_link = myutils.get_publication_query(matched_publications[100 * i: 100 * (i + 1)], clickable=True)
        print("LINK {i}".format(i=i))
        print(clickalbe_link)
        print()

    #  other_query = 'https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q='
    #  id_template = 'id%3A{id}'
    #  chosen_format = '&format={format_name}'.format(
    #      format_name=parsed_args["format"])
    #  test_query = other_query + id_template + chosen_format
    #  my_query = test_query.format(size=size, page='1', id=collected_ids[0])


if __name__ == "__main__":
    main(sys.argv[1:])
