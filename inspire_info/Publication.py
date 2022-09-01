from inspire_info.Author import Author
import datetime

class Publication(object):

    def __init__(self, publication):
        self.publication = publication
        self.meta = publication["metadata"]
        self.links = publication["links"]
        self.created = publication["created"]
        self.updated = publication["updated"]

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