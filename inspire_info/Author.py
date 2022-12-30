__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'


class Author(object):

    def __init__(self, author):
        self.author = author
        self.full_name = author["full_name"]
        self.uuid = author["uuid"]

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

    @property
    def bai(self):
        if "ids" in self.author.keys():
            for id in self.author["ids"]:
                if id["schema"] == "INSPIRE BAI":
                    return id["value"]
        return None

    def __repr__(self):
        return "Author(" + self.full_name + ")"
