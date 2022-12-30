__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

from inspire_info.Author import Author
import datetime
import os


class Publication(object):

    def __init__(self, publication):
        self.publication = publication
        self.meta = publication["metadata"]
        self.links = publication["links"]
        self.created = publication["created"]
        self.updated = publication["updated"]

        self.authors = self.meta.get("authors", [])
        self.author_objects = [Author(author) for author in self.authors]
        self.author_names = [auth.full_name for auth in self.author_objects]
        self.author_uuids = [auth.uuid for auth in self.author_objects]
        self.author_bais = [auth.bai for auth in self.author_objects]

        self.id = publication["id"]
        self.earliest_date = self.meta["earliest_date"]
        self.title = self.meta["titles"][0]["title"]
        if "-" in self.earliest_date:
            self.earliest_date = self.earliest_date.split("-")[0]

        datetime_object = datetime.datetime.strptime(self.earliest_date, '%Y')
        self.earliest_date_year = datetime_object.year
        if "collaborations" in self.meta:
            self.collaborations = [item["value"]
                                   for item in self.meta["collaborations"]]
        else:
            self.collaborations = []
        self.matched = False

    def __repr__(self):
        return "Publication(" + self.title + ")"

    @property
    def keywords(self):
        if "keywords" in self.meta:
            return [item["value"].lower() for item in self.meta["keywords"]]
        else:
            return None

    def downloaded_file(self, link_type="bibtex"):
        return os.path.split(self.links[link_type])[-1]

    @property
    def downloaded_bibtex_file(self):
        return self.downloaded_file(link_type="bibtex")
