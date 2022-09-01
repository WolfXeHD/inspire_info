import inspire_info.myutils as myutils
import inspire_info.Publication as Publication
from urllib.parse import quote
import os
import math

class InspireInfo(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = myutils.read_config(self.config_path)
        self.has_data = False

        if "cache_file" not in self.config:
            self.cache_file = os.path.abspath(self.config_path).replace(
                ".yaml", ".pkl")
        else:
            self.cache_file = self.config["cache_file"]
        self.config["cache_file"] = self.cache_file

        if "name_proposal" not in self.config:
            self.name_proposal = self.config_path.replace(".yaml",
                                                          "_name_proposal.txt")
        else:
            self.name_proposal = self.config["name_proposal"]

        self.institute_and_time_query = myutils.build_query_template(
            lower_date=self.config["lower_date"],
            upper_date=self.config["upper_date"])

        self.global_query = self.institute_and_time_query.format(
            page='1', size=str(self.config["size"]), institute=quote(self.config["institute"]))

    def get_data(self, retrieve=False):
        self.data = myutils.get_data(
            global_query=self.global_query,
            retrieve=retrieve,
            institute_and_time_query=self.institute_and_time_query,
            config=self.config
        )
        self.has_data = True

        print("Creating Publication now...")
        self.publications = [Publication(pub) for pub in self.data["hits"]["hits"]]

    def write_data(self):
        myutils.write_data(data=self.data, filename=self.cache_file)

    def write_name_proposal(self):
        print("Writing out", self.name_proposal)
        with open(self.name_proposal, "w") as f:
            for name in sorted(self.name_proposal_data):
                f.write(name + "\n")

    def match_publications_by_keywords(self, keywords=None):
        if not self.has_data:
            self.get_data()

        if keywords is None:
            keywords = self.config["keywords"]

        self.publications_without_keywords, self.matched_publications, self.unmatched_publications = myutils.match_publications_by_keywords(
            self.publications, keywords)

        return self.publications_without_keywords, self.matched_publications, self.unmatched_publications

    def match_authors(self, publications):
        matched_authors = myutils.get_matched_authors(publications=publications,
                                                 institute=self.config["institute"],
                                                 people_to_exclude=self.config["people_to_exclude"])

        return matched_authors

    def get_clickable_links(self, match_type):
        if match_type not in ["matched", "unmatched", "no_keywords"]:
            raise ValueError("match_type must be one of ['matched', 'unmatched', 'no_keywords']")

        if match_type == "matched":
            publications = self.matched_publications
        elif match_type == "unmatched":
            publications = self.unmatched_publications
        else:
            if hasattr(self, "publications_without_keywords"):
                publications = self.publications_without_keywords
            else:
                raise ValueError("No publications_without_keywords found")
        return myutils.get_clickable_links(publications=publications)
        
    def print_clickable_links(self, match_type):
        clickable_links = self.get_clickable_links(match_type) 
        for idx, link in enumerate(clickable_links):
            print("LINK:", idx)
            print(link)

    def read_name_proposal(self):
        with open(self.name_proposal, "r") as f:
            self.name_proposal_data = [line.strip() for line in f]

    def match_publications_by_authors(self, authors=None):
        if not self.has_data:
            self.get_data()

        if authors is None:
            authors = self.name_proposal_data
        self.matched_publications, self.unmatched_publications = myutils.match_publications_by_authors(self.publications, 
                                              name_proposal_data=authors,
                                              institute=self.config["institute"],)
        return self.matched_publications, self.unmatched_publications