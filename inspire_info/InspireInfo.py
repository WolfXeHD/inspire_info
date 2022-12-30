__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import datetime
import json
import os
import shutil
from urllib.parse import quote

import tqdm

import inspire_info.myutils as myutils
from inspire_info.Publication import Publication


class InspireInfo(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_dir = os.path.dirname(self.config_path)
        self.config = myutils.read_config(self.config_path)
        self.has_data = False
        self.link_type = self.config.get("link_type", "bibtex")
        self.data = None
        self.publications = []

        self.authors = self.config["authors"]
        self.authors_output_dir = self.config.get(
            "authors_output_dir", "authors")
        self.authors_output_dir = os.path.join(self.config_dir, "..", self.authors_output_dir)
        self.author_file_template = "author_{author}.txt"

        self.collaborations = self.config["collaborations"]
        self.earliest_date_collaboration_check = self.config["earliest_date_collaboration_check"]

        if "cache_file" not in self.config:
            self.cache_file = os.path.abspath(self.config_path).replace(
                ".yaml", ".pkl")
        else:
            self.cache_file = self.config["cache_file"]
        self.config["cache_file"] = self.cache_file
        self.publications_to_block = self.config.get("publications_to_block", [])

        self.institute_and_time_query = myutils.build_query_template(
            lower_date=self.config["lower_date"],
            upper_date=self.config["upper_date"],
            add_collaborations=self.collaborations,
            add_institute=True
        )

        self.global_query = self.institute_and_time_query.format(
            page='1', size=str(self.config["size"]), institute=quote(self.config["institute"]))

    @property
    def cache_exists(self):
        """Checks if the cache-file exists.

        Returns:
            bool: True if the cache-file exists, False otherwise.
        """
        return os.path.exists(self.cache_file)

    @property
    def matched_publications(self):
        """Returns the list of matched publications.

        Returns:
            list: List of Publication objects.
        """
        if self.publications is not None:
            matched_publications = []
            for pub in self.publications:
                if pub.matched:
                    matched_publications.append(pub)
            return matched_publications
        else:
            return None

    @property
    def downloaded_bibtex_files(self):
        files = []
        for pub in self.matched_publications:
            if pub.matched:
                files.append(pub.downloaded_bibtex_file)
        return files

    @property
    def author_bais(self):
        filelist = []
        for author in self.authors:
            author_file = os.path.join(
                self.authors_output_dir, self.author_file_template.format(author=author))
            filelist.append(author_file)

        self.download_missing_authors()
        bais_to_check = myutils.get_inspire_bais_from_filelist(filelist)
        return bais_to_check

    def get_data(self, retrieve=False):
        """This function retrieves the inspire data and stores it in self.data, which is a
        dictionary. It also creates a list of Publication objects, which are stored in self.
        publications. The Publication objects are created from the data in self.data.
        The query which is executed consists of the query for the institute and the time.
        No keywords are used for this query.

        Args:
            retrieve (bool, optional): This option allows to read the data from a cache-file
            (False) or execute a query to inspire (True). Defaults to False.
        """
        if retrieve:
            print("Retrieving data from inspire...")
        self.data = myutils.get_data(
            global_query=self.global_query,
            retrieve=retrieve,
            institute_and_time_query=self.institute_and_time_query,
            config=self.config
        )
        self.has_data = True

        print("Creating Publication now...")
        self.publications = [Publication(pub)
                             for pub in self.data["hits"]["hits"]]

    def write_data(self):
        """Writes the data stored in self.data to a cache-file, named self.cache_file.
        """
        myutils.write_data(data=self.data, filename=self.cache_file)

    def get_clickable_links(self):
        return myutils.get_clickable_links(publications=self.matched_publications)

    def print_clickable_links(self):
        clickable_links = self.get_clickable_links()
        for idx, link in enumerate(clickable_links):
            print("LINK:", idx)
            print(link)

    def match_publications_by_authors(self):
        """This function matches the publications in self.publications to the authors in
        self.authors based on the inspire BAI. Additionally, the affiliation of the author is
        checked. If the affiliation matches the institute, the publication is added to the list of
        matched publications, i.e flagged as 'matched' (see Publication class). The list of matched
        publications is returned.

        Returns:
            list: List of Publication objects which is matched
        """
        if not self.has_data:
            self.get_data()

        matched_publications = []
        for pub in self.publications:
            if pub.matched:
                continue
            matched = False
            for author_to_check in self.author_bais:
                if author_to_check in pub.author_bais:
                    idx = pub.author_bais.index(author_to_check)
                    candidate_author = pub.author_objects[idx]
                    if candidate_author.affiliations is not None:
                        for affiliation in candidate_author.affiliations:
                            if affiliation == self.config["institute"]:
                                matched_publications.append(pub)
                                matched = True
                                pub.matched = True
                                break
                if matched:
                    break
        return matched_publications

    def match_publications_by_collaborations(self):
        """This function matches the publications in self.publications to the collaborations in
        self.collaborations. The earliest date of the publication is checked against the earliest
        date of the collaboration check. If the publication is older than the earliest date of the
        collaboration check, the publication is not matched. The list of matched publications is
        returned.

        Returns:
            list: List of Publication objects which is matched.
        """
        if not self.has_data:
            if self.cache_exists:
                self.get_data(retrieve=False)
            else:
                self.get_data(retrieve=True)

        matched_publications = []
        for pub in self.publications:
            if pub.matched:
                continue
            if pub.collaborations is not None:
                for collaboration in self.collaborations:
                    if ((collaboration in pub.collaborations) and
                            (pub.earliest_date_year >= self.earliest_date_collaboration_check)):
                        if len(pub.authors) > 0:
                            for auth in pub.author_objects:
                                if auth.bai in self.author_bais:
                                    matched_publications.append(pub)
                                    pub.matched = True
                                    break
                        else:
                            pub.matched = True
                        matched_publications.append(pub)
                        break
        return matched_publications

    def download_publications(self, publications, link_type=None, target_dir=None):
        """This function downloads the `publications` to the `target_dir`. If `link_type` is not
        specified, the link_type from the config file is used. If `target_dir` is not specified,
        the `link_type` is used. The tarball is named `publications_{link_type}_{date}.tar.gz`.

        Raises:
            ValueError: link_type must be one of ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv',
            'citations']

        Args:
            publications (list of Publications): List of publications which should be downloaded.
            link_type (str, optional): type of data which should be downloaded. Defaults to None
            and then uses the link_type from the config file or 'bibtex' if nothing is specified.
            target_dir (str, optional): directory to which the publications are going to be stored.
            Defaults to None and then uses the `link_type`.
        """
        if link_type is None:
            link_type = self.link_type
        if target_dir is None:
            target_dir = link_type

        if link_type not in ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv',
                             'citations']:
            raise ValueError(
                """link_type must be one of ['bibtex', 'latex-eu', 'latex-us', 'json', 'cv',
                'citations']""")
        print("Downloading", link_type, "files to", target_dir)

        # what is today's date?
        tarball_name = "publications_{}_{}.tar.gz".format(
            link_type, datetime.datetime.now().strftime("%Y-%m-%d"))
        myutils.get_tarball_of_publications(publications=publications,
                                            link_type=link_type,
                                            target_dir=target_dir,
                                            tarball_name=tarball_name)

    def check_missing_publications_on_disk(self, publications, link_type=None, target_dir=None):
        """This function checks if the publications are already on disk. If not, it downloads them.

        Args:
            publications (list of Publiations): List of publications which should be checked.
            link_type (str, optional): type of data which should be downloaded. Defaults to None
            and then takes the link_type from the config file or 'bibtex' if nothing is specified.
            target_dir (str, optional): Folder which is going to be checked for input. Defaults to
            None and then uses the `link_type`.

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

    def search_authors_and_download(self, authors_output_dir=None, author=None):
        """This function searches for the authors in Inspire and downloads the data to the
        `authors_output_dir`. If `author` is not specified, all authors in the config file are

        Args:
            authors_output_dir (str, optional): _description_. Defaults to "authors".
            author (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """

        if author is None:
            authors = self.authors
        else:
            authors = [author]
        if authors is None:
            raise ValueError(
                "Please set the authors in your config or set the authors of your InspireInfo.")
        if authors_output_dir is None:
            authors_output_dir = self.authors_output_dir

        print("Saving authors to directory: {}".format(authors_output_dir))
        if not os.path.exists(authors_output_dir):
            os.makedirs(authors_output_dir)

        print("Searching for authors")
        for author in tqdm.tqdm(authors):
            query = myutils.build_person_query(author, size=5)
            data = myutils.read_from_inspire(query, silent=True)
            path_to_save = os.path.join(
                authors_output_dir, self.author_file_template.format(author=author))
            with open(path_to_save, "w") as f:
                json.dump(data, f)

    def block_publications(self):
        for pub in self.publications:
            if pub.matched and str(pub.id) in self.publications_to_block:
                print("Blocking publication", pub.id, pub.title)
                pub.matched = False

    def get_papers(self, lower_date, upper_date, download, target_dir, refresh):
        """Function to download the bibtex files of the publications of the authors and
        collaborations. The publications are downloaded to the `target_dir`. If `refresh` is set to
        True, the `target_dir` is deleted before downloading the publications. If `download` is set
        to 'bibtex' or 'latex-eu' or 'latex-us', the publications are downloaded in the specified
        format. lower_date and upper_date are used to filter the publications loaded from the cache.


        Args:
            lower_date (str): lower date of the publication date range, i.e. '2019-01-01'
            upper_date (str): upper date of the publication date range, i.e. '2020-01-01'
            download (str): type of data which should be downloaded. Must be one of ['bibtex',
            'latex-eu', 'latex-us', 'json', 'cv', 'citations', 'None']
            target_dir (str): directory to which the publications are going to be stored.
            refresh (bool): if True, the `target_dir` is deleted before downloading the
            publications.

        Raises:
            FileNotFoundError: if cache-file does not exist.
        """
        print("Overwriting lower_date and upper_date in config with: {} {}".format(
            lower_date, upper_date))

        self.config["lower_date"] = lower_date
        self.config["upper_date"] = upper_date

        if self.cache_exists:
            self.get_data(retrieve=False)
        else:
            raise FileNotFoundError("Please create a cache-file first.")

        self.match_publications_by_authors()
        self.match_publications_by_collaborations()
        self.block_publications()
        self.print_clickable_links()

        if refresh and os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        missing_publications = self.check_missing_publications_on_disk(
            self.matched_publications, link_type=download, target_dir=target_dir)

        if download != "None":
            self.download_publications(
                publications=missing_publications,
                link_type=download,
                target_dir=target_dir
            )

    def download_missing_authors(self):
        """Downloads the missing author files. Author files are needed to execute a search for the
        BAI of the authors
        """
        for author in self.authors:
            author_file = os.path.join(
                self.authors_output_dir, self.author_file_template.format(author=author))
            if not os.path.exists(author_file):
                print("Author file {} does not exist. Downloading it.".format(
                    author_file))
                self.search_authors_and_download(
                    authors_output_dir=self.authors_output_dir, author=author)

    @property
    def conversion_style_to_html(self):
        """Returns the full path to the conversion style for html."""
        abs_config_path = os.path.abspath(self.config_path)
        return os.path.join(os.path.dirname(abs_config_path),
                            self.config["conversion_style_to_html"])
