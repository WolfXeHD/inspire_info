import requests
import time
import datetime
import yaml
from urllib.parse import quote
import json
import tqdm

def read_config(file_to_read):
    with open(file_to_read, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config

def read_from_inspire(formatted_query):
    response = requests.get(formatted_query)
    while response.status_code != 200:
        response = requests.get(formatted_query)
        #  response.raise_for_status()  # raises exception when not a 2xx response
        time.sleep(1.0)
        print("retrieving failed, with status code: " +
              str(response.status_code))
        print("query is:")
        print(formatted_query)
        print("trying again...")
    else:
        data = response.json()
        print("data retrieved.")
    return data


def get_publication_query(publications, clickable):
    ids = []
    for publication in publications:
        ids.append(publication.id)
    result = get_publication_by_id(id_list=ids)
    if not clickable:
        return result
    else:
        return result.replace("api/", "").replace("fields=titles,authors,id",
                                                  "")


def get_publication_by_id(id_list, size=500):
    other_query = 'https://inspirehep.net/api/literature?fields=titles,authors,id&sort=mostrecent&size={size}&page={page}&q='
    id_template = 'recid%3A{id} or '

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

def build_query_template(lower_date, upper_date):
    # building query command
    institute_query = 'https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=aff:{institute}'
    time_query = build_time_query(
        lower_date=lower_date,
        upper_date=upper_date)
    if time_query != "":
        institute_and_time_query = institute_query + " and " + time_query
    else:
        institute_and_time_query = institute_query

    institute_and_time_query = institute_and_time_query.replace(" ", "%20")
    institute_and_time_query = institute_and_time_query.replace("\n", "")
    return institute_and_time_query


def get_matched_authors(publications, institute, people_to_exclude):
    all_authors = []
    for pub in publications:
        for author in pub.authors:
            auth = Author(author)
            if auth.affiliations is not None and institute in auth.affiliations:
                for name in people_to_exclude:
                    if name in auth.full_name:
                        print("excluding: " + auth.full_name, "with publication", pub.title)
                        break
                    all_authors.append(auth)

    all_authors_named = list(
        set([auth.full_name for auth in all_authors]))
    return all_authors_named


def get_data(global_query, retrieve, institute_and_time_query, config):
    if retrieve:
        # retrieving data
        data = read_from_inspire(formatted_query=global_query)
        total_hits = data["hits"]["total"]
        n_pages = int(total_hits / int(config["size"])) + 1
        for i in tqdm.tqdm(range(n_pages)):
            if i > 0:
                time.sleep(1.0)
                this_query = institute_and_time_query.format(
                    page=str(i + 1),
                    size=str(config["size"]),
                    institute=quote(config["institute"]))
                temp_data = read_from_inspire(
                    formatted_query=this_query)
                data["hits"]["hits"] += temp_data["hits"]["hits"]

        with open(config["cache_file"], "w") as f:
            json.dump(data, f)
    else:
        print("Loading data...")
        with open(config["cache_file"], "r") as f:
            data = json.load(f)
        total_hits = data["hits"]["total"]
    return data


class InspireInfo(object):
    def __init__(self, data):
        self.data = data


class Publication(object):
    def __init__(self, publication):
        self.publication = publication
        self.meta = publication["metadata"]
        self.authors = self.meta["authors"]

        self.author_objects = [Author(author) for author in self.authors]
        self.author_names = [auth.full_name for auth in self.author_objects]
        self.id = publication["id"]
        self.earliest_date = self.meta["earliest_date"]
        self.title = self.meta["titles"][0]["title"]
        if "-" in self.earliest_date:
            self.earliest_date = self.earliest_date.split("-")[0]

        datetime_object = datetime.datetime.strptime(self.earliest_date, '%Y')
        self.earliest_date_year = datetime_object.year

    def __repr__(self):
        return "Publication(" + self.title + ")"

    @property
    def keywords(self):
        if "keywords" in self.meta:
            return [item["value"].lower() for item in self.meta["keywords"]]
        else:
            return None

class Author(object):
    def __init__(self, author):
        self.author = author
        self.full_name = author["full_name"]

    @property
    def affiliations(self):
        if "affiliations" in self.author.keys():
            affiliations = [
                affiliation["value"]
                for affiliation in self.author["affiliations"]
            ]
        elif "raw_affiliations" in self.author.keys():
            affiliations = [
                affiliation["value"]
                for affiliation in self.author["raw_affiliations"]
            ]
        else:
            affiliations = None
        return affiliations

    def __repr__(self):
        return "Author(" + self.full_name + ")"
