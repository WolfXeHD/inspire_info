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
import tqdm



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
    parser.add_argument('--file_to_read',
                        type=str,
                        required=True,
                        help="File containing the search names, will not be used if 'retrieve' is active") # would be better if it was the bai
    parser.add_argument('--retrieve',
                        action='store_true',
                        help="If true API-call is created, otherwise cache-file is going to be used.")
    parser.add_argument('--cache_file',
                        type=str,
                        required=True,
                        help="cache file to store data")

    parser.add_argument('--size',
                        type=int,
                        default=500,
                        help="size of queried package")

    return dict(vars(parser.parse_args()))

def read_from_inspire(formatted_query):
        response = requests.get(formatted_query)
        while response.status_code != 200:
            response = requests.get(formatted_query)
            #  response.raise_for_status()  # raises exception when not a 2xx response
            time.sleep(0.5)
            print("retrieving failed, with status code: " + str(response.status_code))
            print("query is:")
            print(formatted_query)
            print("trying again...")
        else:
            data = response.json()
            print("data retrieved.")
        return data

def get_publication_by_id(id_list, size):
    other_query = 'https://inspirehep.net/api/literature?fields=titles,authors,id&sort=mostrecent&size={size}&page={page}&q='
    id_template = 'id%3A{id} or '

    id_query = ""
    for id in id_list:
        id_query += id_template.format(id=id)
    else:
        id_query = id_query[:-4]
    id_query = id_query.replace(" ", "%20")
    return other_query.format(page='1', size=size) + id_query


def build_time_query(lower_date=None, upper_date=None):
    time_query_low = 'date:>{lower_date}'
    time_query_up = 'date:<{upper_date}'
    if upper_date is not None and lower_date is not None:
        return "(" + time_query_low.format(
            lower_date=lower_date) + " and " + time_query_up.format(
                upper_date=upper_date) + ")"
    elif lower_date is not None:
        return "(" + time_query_low.format(lower_date=lower_date) + ")"
    else:
        return ""


def build_people_query(file_to_read="authors.txt"):
    # This needs to be replaced with the csv from Anja
    with open(file_to_read, "r") as f:
        people_to_match = f.readlines()

    author_query = '(author%3A{name})'
    people_query = ""
    for author in people_to_match:
        people_query += author_query.format(name=author) + " or "
    else:
        people_query = people_query[:-4]
    people_query = people_query.replace(" ", "%20")
    return people_query, people_to_match


def main(arguments):
    parsed_args = parse_args(args=arguments)
    size = parsed_args["size"]

    # building query command
    institute_query = 'https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=aff:{institute}'
    people_query, people_to_match = build_people_query(
        file_to_read=parsed_args["file_to_read"])
    time_query = build_time_query(lower_date=parsed_args["lower_date"],
                                  upper_date=parsed_args["upper_date"])
    if time_query != "":
        total_query = institute_query + " and " + time_query + " and " + people_query
    else:
        total_query = institute_query + " and " + people_query
    total_query = total_query.replace(" ", "%20")
    total_query = total_query.replace("\n", "")
    formatted_query = total_query.format(page='1',
                                         size=str(size),
                                         institute=quote(
                                             parsed_args["institute"]))

    if parsed_args["retrieve"]:
        # retrieving data
        data = read_from_inspire(formatted_query=formatted_query)
        total_hits = data["hits"]["total"]
        n_pages = int(total_hits / int(size)) + 1
        for i in tqdm.tqdm(range(n_pages)):
            if i > 0:
                time.sleep(0.5)
                this_query = total_query.format(page=str(i + 1),
                                       size=str(size),
                                       institute=quote(
                                           parsed_args["institute"]))
                temp_data = read_from_inspire(formatted_query=this_query)
                data["hits"]["hits"] += temp_data["hits"]["hits"]

        with open(parsed_args["cache_file"], "w") as f:
            json.dump(data, f)
    else:
        with open(parsed_args["cache_file"], "r") as f:
            data = json.load(f)
        total_hits = data["hits"]["total"]


    unmachted_publications = []
    collected_ids = []
    for i in tqdm.tqdm(range(total_hits)):
        #  title = data['hits']['hits'][i]['metadata']['titles'][0]['title']
        authors = data['hits']['hits'][i]['metadata']['authors']
        found = False
        for author in authors:
            affiliations = author.get("affiliations", [])
            for aff in affiliations:
                if aff.get("value") == parsed_args["institute"]:
                    for person in people_to_match:
                        this_person = person.replace("\n", "")
                        if this_person in author["name_suggest"]["input"]:
                            found = True
                else:
                    continue
            if found:
                collected_ids.append(data["hits"]["hits"][i]["id"])
                break
        else:
            unmachted_publications.append(data["hits"]["hits"][i]["id"])

    print(total_hits)
    print(len(collected_ids))
    print(len(unmachted_publications))

    unmachted_query = get_publication_by_id(id_list=unmachted_publications, size=size)
    print(unmachted_query)

    matched_query = get_publication_by_id(id_list=collected_ids, size=size)

    #  other_query = 'https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q='
    #  id_template = 'id%3A{id}'
    #  chosen_format = '&format={format_name}'.format(
    #      format_name=parsed_args["format"])
    #  test_query = other_query + id_template + chosen_format
    #  my_query = test_query.format(size=size, page='1', id=collected_ids[0])


if __name__ == "__main__":
    main(sys.argv[1:])
