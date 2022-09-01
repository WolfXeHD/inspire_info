
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