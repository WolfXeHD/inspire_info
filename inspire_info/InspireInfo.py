import datetime
import os
from urllib.parse import quote

import inspire_info.myutils as myutils
from inspire_info.Publication import Publication


class InspireInfo(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = myutils.read_config(self.config_path)
        self.has_data = False
        self.link_type = self.config.get("link_type", "bibtex")
        self.data = None
        self.publications = None
        self.publications_without_keywords = None
        self.name_proposal_data = None
        self.matched_publications = None
        self.unmatched_publications = None

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

    @property
    def cache_exists(self):
        """Checks if the cache-file exists.

        Returns:
            bool: True if the cache-file exists, False otherwise.
        """
        return os.path.exists(self.cache_file)

    def get_data(self, retrieve=False):
        """This function retrievs the inspire data and stores it in self.data, which is a dictionary. It also creates a list of Publication objects, which are stored in self.publications. The Publication objects are created from the data in self.data.
        The query which is executed consists of the query for the institute and the time. No keywords are used for this query.

        Args:
            retrieve (bool, optional): This option allows to read the data from a cache-file (False) or execute a query to inspire (True). Defaults to False.
        """
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
        """Writes the data stored in self.data to a cache-file, named self.cache_file.
        """
        myutils.write_data(data=self.data, filename=self.cache_file)

    def write_name_proposal(self):
        """Writes the name data in self.name_proposal_data to a file, named self.name_proposal.
        """
        print("Writing out", self.name_proposal)
        with open(self.name_proposal, "w") as f:
            for name in sorted(self.name_proposal_data):
                f.write(name + "\n")

    def match_publications_by_keywords(self, keywords=None):
        """The list of publications is matched by keywords, either specified as input (keywors) or read from the config file (self.config["keywords"])

        Args:
            keywords (list, optional): List of keywords for which the division of publications should be carried out. Defaults to None.

        Returns:
            tuple: (publications_without_keywords, matched_publications, unmatched_publications), where
            publications_without_keywords is a list of publications which do not have any keywords,
            matched_publications is a list of publications which have at least one keyword in common with the input keywords/keywords from the config file,
            unmatched_publications is a list of publications which do not have any keywords in common with the input keywords/keywords from the config file.
        """
        if not self.has_data:
            self.get_data()

        if keywords is None:
            keywords = self.config["keywords"]

        self.publications_without_keywords, self.matched_publications, self.unmatched_publications = myutils.match_publications_by_keywords(
            self.publications, keywords)

        return self.publications_without_keywords, self.matched_publications, self.unmatched_publications

    def match_authors(self, publications):
        """This function allows to find the authors of a list of publications which match the institute and excludes people_to_exclude specified in the config file.

        Args:
            publications (Publication): List of publications among which the authors should be found.

        Returns:
            list: List of authors' full name which match the institute and are not in people_to_exclude.
        """
        matched_authors = myutils.get_matched_authors(publications=publications,
                                                 institute=self.config["institute"],
                                                 people_to_exclude=self.config["people_to_exclude"])

        return matched_authors

    def get_clickable_links(self, match_type):
        """This function generates clickalbe links for an inspire query in the browser

        Args:
            match_type (str): One of "matched", "unmatched", "no_keywords". Depending on the value, the function returns clickable links for the matched publications, unmatched publications or publications without keywords.

        Raises:
            ValueError: Raised if input match_type is not one of "matched", "unmatched", "no_keywords".

        Returns:
            str: Clickable links for the inspire query in the browser.
        """
        if match_type not in ["matched", "unmatched", "no_keywords"]:
            raise ValueError("match_type must be one of ['matched', 'unmatched', 'no_keywords']")

        if match_type == "matched":
            publications = self.matched_publications
        elif match_type == "unmatched":
            publications = self.unmatched_publications
        else:
            if hasattr(self, "publications_without_keywords"):
                publications = self.publications_without_keywords
        return myutils.get_clickable_links(publications=publications)

    def print_clickable_links(self, match_type):
        """Executes get_clickable_links and prints the result.

        Args:
            match_type (str): One of "matched", "unmatched", "no_keywords". Depending on the value, the function returns clickable links for the matched publications, unmatched publications or publications without keywords.
        """
        clickable_links = self.get_clickable_links(match_type)
        for idx, link in enumerate(clickable_links):
            print("LINK:", idx)
            print(link)

    def read_name_proposal(self, path_to_read=None):
        """Reads name proposal from a txt-file, from an excel file or from self.name_proposal. Data is stored in self.name_proposal_data.

        Args:
            path_to_read (str, optional): If provided that is the path which is going to be read. Defaults to None.

        Raises:
            ValueError: if path_to_read does not end with .xlsm or .txt
        """
        if path_to_read is None:
            print("Reading:", self.name_proposal)
            with open(self.name_proposal, "r") as f:
                self.name_proposal_data = [line.strip() for line in f]
        elif path_to_read.endswith("xlsm"):
            self.name_proposal_data = myutils.build_name_proposal_from_excel(path_to_read)
        elif path_to_read.endswith("txt"):
            with open(path_to_read, "r") as f:
                self.name_proposal_data = [line.strip() for line in f]
        else:
            raise ValueError("path_to_read must end with .xlsm or .txt")

    def match_publications_by_authors(self, bais_to_check_against):
        if not self.has_data:
            self.get_data()

        self.matched_publications, self.unmatched_publications = myutils.match_publications_by_authors(self.publications,
                                              bais_to_check_against=bais_to_check_against,
                                              institute=self.config["institute"],)
        return self.matched_publications, self.unmatched_publications

    def download_publications(self, publications, link_type=None, target_dir=None):
        """This function downloads the `publications` to the `target_dir`. If `link_type` is not specified, the link_type from the config file is used. If `target_dir` is not specified, the `link_type` is used. The tarball is named `publications_{link_type}_{date}.tar.gz`.

        Raises:
            ValueError: link_type must be one of ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv', 'citations']

        Args:
            publications (list of Publications): List of publications which should be downloaded.
            link_type (str, optional): type of data which should be downloaded. Defaults to None and then uses the link_type from the config file or 'bibtex' if nothing is specified.
            target_dir (str, optional): directory to which the publications are going to be stored. Defaults to None and then uses the `link_type`.
        """
        if link_type is None:
            link_type = self.link_type
        if target_dir is None:
            target_dir = link_type

        if link_type not in ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv',
                            'citations']:
            raise ValueError("link_type must be one of ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv', 'citations']")
        print("Downloading", link_type, "files to", target_dir)

        # what is today's date?
        tarball_name = "publications_{}_{}".format(link_type, datetime.datetime.now().strftime("%Y-%m-%d"))
        myutils.get_tarball_of_publications(publications=publications,
                                            link_type=link_type,
                                            target_dir=target_dir,
                                            tarball_name=tarball_name)

    def check_missing_publications_on_disk(self, publications, link_type=None, target_dir=None):
        """This function checks if the publications are already on disk. If not, it downloads them.

        Args:
            publications (list of Publiations): List of publications which should be checked.
            link_type (str, optional): type of data which should be downloaded. Defaults to None and then takes the link_type from the config file or 'bibtex' if nothing is specified.
            target_dir (str, optional): Folder which is going to be checked for input. Defaults to None and then uses the `link_type`.

        Returns:
            list of Publications: List of publications which are not on disk.
        """
        if target_dir is None:
            if link_type is None:
                target_dir = self.link_type
            else:
                target_dir = link_type

        return myutils.check_missing_publications_on_disk(
            publications=publications,
            link_type=link_type,
            target_dir=target_dir)
