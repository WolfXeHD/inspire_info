__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import datetime
import json
import math
import os
import pickle
import re
import time
from itertools import compress
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
import tqdm
import yaml


def read_config(file_to_read):
    with open(file_to_read, "r", encoding='ISO-8859-1') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def read_authors(authors_file):
    with open(authors_file, "r", encoding='unicode-escape') as f:
        authors = [line.strip() for line in f]
    return authors


def read_from_inspire(formatted_query, silent=False):
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
    data = response.json()
    if not silent:
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
    other_query = 'https://inspirehep.net/api/literature?fields=titles,authors,id'
    other_query += '&sort=mostrecent&size={size}&page={page}&q='
    id_template = 'recid%3A{id} or '

    id_query = ""
    for pub_id in id_list:
        id_query += id_template.format(id=pub_id)
    id_query = id_query[:-4]
    id_query = id_query.replace(" ", "%20")
    return other_query.format(page='1', size=size) + id_query


def build_time_query(lower_date=None, upper_date=None):
    time_query_low = 'date>{lower_date}'
    time_query_up = 'date<{upper_date}'
    if upper_date is not None and lower_date is not None:
        return time_query_low.format(
            lower_date=lower_date) + "%20and%20" + time_query_up.format(
                upper_date=upper_date)
    elif lower_date is not None:
        return time_query_low.format(lower_date=lower_date)
    else:
        return ""


def build_person_query(person, size=25, search_type="authors"):
    if search_type not in ["authors", "literature"]:
        raise ValueError("search_type must be either authors or literature")

    query_template = build_query_template(lower_date=None,
                                          upper_date=None,
                                          add_institute=False,
                                          search_type=search_type)
    query_template += "&q={person}".format(person=quote(person))
    query_template = query_template.format(size=size, page=1)
    return query_template


def build_query_template(lower_date,
                         upper_date,
                         add_institute=True,
                         search_type="literature",
                         add_collaborations=None):
    # building query command
    query = 'https://inspirehep.net/api/{search_type}?sort=mostrecent&size={size}&page={page}'
    query += '&q=('

    if add_institute:
        query += "aff:{institute}"

    if add_collaborations is not None:
        collaborations_query = " or ".join(
            ["collaboration:" + collaboration for collaboration in add_collaborations])
        collaborations_query = "(" + collaborations_query + ")"
        if not add_institute:
            query += collaborations_query + ")"
        else:
            query += " or " + collaborations_query + ")"
    else:
        query += ")"

    time_query = build_time_query(lower_date=lower_date, upper_date=upper_date)
    time_query = "(" + time_query + ")"
    if time_query != "()":
        if query.endswith("&q=()"):
            institute_and_time_query = query[:-2] + time_query
        else:
            institute_and_time_query = query + " and " + time_query
    else:
        institute_and_time_query = query

    if institute_and_time_query.endswith("&q=()"):
        institute_and_time_query = institute_and_time_query.replace(
            "&q=()", "")

    matches = re.findall(r'\{(.*?)\}', institute_and_time_query)
    replace_dict = {}
    for match in matches:
        if match != "search_type":
            replace_dict[match] = "{" + match + "}"
        else:
            replace_dict[match] = search_type
    institute_and_time_query = institute_and_time_query.format(
        **replace_dict)

    institute_and_time_query = institute_and_time_query.replace(" ", "%20")
    institute_and_time_query = institute_and_time_query.replace("\n", "")
    return institute_and_time_query


def get_data(global_query, retrieve, institute_and_time_query, config):
    if retrieve:
        # retrieving data
        data = read_from_inspire(formatted_query=global_query, silent=True)
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
                    formatted_query=this_query, silent=True)
                data["hits"]["hits"] += temp_data["hits"]["hits"]
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
        masker_low = np.array([True] * len(df))

    if config["upper_date"] is not None:
        masker_up = df["earliest_date"] < config["upper_date"]
    else:
        masker_up = np.array([True] * len(df))

    masker = masker_low & masker_up

    filtered_list = list(compress(data["hits"]["hits"], masker))
    data["hits"]["total"] = len(filtered_list)
    data["hits"]["hits"] = filtered_list
    return data, df[masker]


def get_tarball_of_publications(publications, link_type, target_dir, tarball_name):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    ids = []
    for pub in publications:
        link = pub.links[link_type]
        ids.append(pub.id)
        cmd = "wget -P {target_dir} {link}".format(target_dir=target_dir,
                                                   link=link)
        os.system(cmd)
    print("Downloaded {} publication files".format(len(ids)))

    # Create tarball of all files
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


def get_clickable_links(publications):
    clickable_links = []
    for i in range(math.ceil(len(publications) / 100)):
        print(100 * i, 100 * (i + 1))
        print(len(publications[100 * i:100 * (i + 1)]))

        clickalbe_link = get_publication_query(
            publications[100 * i:100 * (i + 1)], clickable=True)
        clickable_links.append(clickalbe_link)
    return clickable_links


def check_missing_publications_on_disk(publications, target_dir, link_type):
    missing_publications = []
    for pub in publications:
        path_to_check = os.path.join(
            target_dir, pub.downloaded_file(link_type))
        print(path_to_check)
        if not os.path.exists(path_to_check):
            missing_publications.append(pub)
    return missing_publications


def build_name_proposal_from_excel(path_to_excel):
    df = pd.read_excel(path_to_excel)
    name_proposal_data = []
    for i in range(len(df)):
        data = df.iloc[i]["inspire_names"]
        splitted_data = data.split(";")
        for split in splitted_data:
            name_proposal_data.append(split)
    return name_proposal_data


def get_inspire_bai(file):
    with open(file, "r") as f:
        data = json.load(f)
    l_bais = []
    for idx, item in enumerate(data["hits"]["hits"]):
        if "ids" in item["metadata"]:
            schemas = [id["schema"] for id in item["metadata"]["ids"]]
            if "INSPIRE BAI" not in schemas:
                print("No INSPIRE BAI")
            else:
                idx_scheme = schemas.index("INSPIRE BAI")
                bai = item["metadata"]["ids"][idx_scheme]["value"]
                l_bais.append(bai)
        else:
            print("No ids found")
        if idx > 4:
            break
    return l_bais


def get_inspire_bais_from_filelist(filelist):
    l_bais = []
    for file in filelist:
        l_bais += get_inspire_bai(file)
    return l_bais


def ensure_dirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
