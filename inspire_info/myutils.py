import datetime
import time
from urllib.parse import quote

import requests
import tqdm
import yaml
import pickle
import pandas as pd
import os
from itertools import compress


def read_config(file_to_read):
    with open(file_to_read, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def read_from_inspire(formatted_query):
    response = requests.get(formatted_query)
    while response.status_code != 200:
        time.sleep(1.0)
        print("retrieving failed, with status code: " +
              str(response.status_code))
        print("query is:")
        print(formatted_query)
        print("trying again...")

        response = requests.get(formatted_query)
        #  response.raise_for_status()  # raises exception when not a 2xx response
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
    time_query_low = 'date>{lower_date}'
    time_query_up = 'date<{upper_date}'
    if upper_date is not None and lower_date is not None:
        return time_query_low.format(
            lower_date=lower_date) + " and " + time_query_up.format(
                upper_date=upper_date)
    elif lower_date is not None:
        return time_query_low.format(lower_date=lower_date)
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
    time_query = build_time_query(lower_date=lower_date, upper_date=upper_date)
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
        for auth in pub.author_objects:
            if auth.affiliations is not None and institute in auth.affiliations:
                for name in people_to_exclude:
                    if name in auth.full_name:
                        print("excluding: " + auth.full_name,
                              "with publication", pub.title)
                        break
                else:
                    all_authors.append(auth)

    all_authors_named = list(set([auth.full_name for auth in all_authors]))
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
                temp_data = read_from_inspire(formatted_query=this_query)
                data["hits"]["hits"] += temp_data["hits"]["hits"]
        else:
            data, df = apply_cleaning_to_data(data=data, config=config)
    else:
        data = read_data(filename=config["cache_file"])
        data, df = apply_cleaning_to_data(data=data, config=config)
        total_hits = data["hits"]["total"]
    return data


def read_data(filename):
    print("Reading data...")
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data


def write_data(filename, data):
    print("Writing data...")
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def get_earliest_date(row):
    if "earliest_date" in row["metadata"]:
        return row["metadata"]["earliest_date"]
    else:
        return None


def apply_cleaning_to_data(data, config):
    df = convert_to_pandas(data)
    if config["lower_date"] is not None:
        masker_low = df["earliest_date"] > config["lower_date"]
    else:
        masker_low = [True] * len(df)

    if config["upper_date"] is not None:
        masker_up = df["earliest_date"] < config["upper_date"]
    else:
        masker_up = [True] * len(df)

    masker = masker_low & masker_up

    filtered_list = list(compress(data["hits"]["hits"], masker))
    data["hits"]["total"] = len(filtered_list)
    data["hits"]["hits"] = filtered_list
    return data, df[masker]


def get_tarball_of_publications(publications, link_type, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    ids = []
    for pub in publications:
        link = pub.links[link_type]
        ids.append(pub.id)
        cmd = "wget -P {target_dir} {link}".format(target_dir=target_dir,
                                                   link=link)
        os.system(cmd)
    else:
        print("Downloaded {} publication files".format(len(ids)))

    # Create tarball of all files
    tarball_name = "publications.tar.gz"
    cmd = "tar -czvf {tarball_name} -C {target_dir} .".format(
        tarball_name=tarball_name, target_dir=target_dir)
    os.system(cmd)


def convert_to_pandas(data):
    df = pd.DataFrame(data["hits"]["hits"])
    updated_date = df.apply(lambda row: datetime.datetime.strptime(
        row["updated"], "%Y-%m-%dT%H:%M:%S.%f+00:00"),
                            axis=1)
    created_date = df.apply(
        lambda row: datetime.datetime.strptime(row["created"][:4], "%Y"),
        axis=1)
    df["updated_date"] = pd.to_datetime(updated_date)
    df["created_date"] = pd.to_datetime(created_date)
    earliest_date = df.apply(lambda row: get_earliest_date(row=row), axis=1)
    df["earliest_date"] = pd.to_datetime(earliest_date)
    return df


class InspireInfo(object):
    def __init__(self, data):
        self.data = data