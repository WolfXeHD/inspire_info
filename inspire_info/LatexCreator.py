__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import os
import glob
import logging as log
from bs4 import BeautifulSoup

from inspire_info import myutils


class LatexCreator:
    """This class creates a latex document with a bibliography from a template and a folder with
    bibtex files.
    """
    def __init__(self,
                 template,
                 source_folder,
                 filename,
                 bibtex_list=None,
                 outdir=None,
                 conversion_style_to_html=None,
                 pandoc_command="pandoc"
                 ):
        self.template = template
        if outdir is None:
            self.outdir = os.path.join(
                os.path.dirname(source_folder),
                "latex_" + os.path.basename(source_folder))
        else:
            self.outdir = outdir
        self.source_folder = source_folder
        self.bibtex_list = bibtex_list
        self.keys = []
        self.filename = filename
        self.conversion_style_to_html = conversion_style_to_html
        self.pandoc_command = pandoc_command
        self.html_file = os.path.join(self.outdir, self.filename.replace(".tex", ".html"))
        self.html_body_file = os.path.join(self.outdir,
                                           "body_" + self.filename.replace(".tex", ".html"))

        myutils.ensure_dirs(dirs=[self.outdir])

    def create_latex_doc(self, filename=None):
        if filename is None:
            filename = self.filename
        cwd = os.getcwd()
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        os.chdir(self.outdir)
        nocite_string = ""
        for key in self.keys:
            nocite_string += r"\nocite{" + key + "}\n"
        this_template = self.template.replace("__NOCITES__", nocite_string)
        print(this_template)

        with open(filename, "w") as f:
            f.write(this_template)

        # compile template.tex to template.pdf
        os.system(f"pdflatex -interaction=nonstopmode {filename}")
        os.system(
            "bibtex {filename}".format(filename=filename.replace(".tex", "")))
        os.system(f"pdflatex -interaction=nonstopmode {filename}")
        os.system(f"pdflatex -interaction=nonstopmode {filename}")
        os.chdir(cwd)

    def make_bibliography(self, filename="references.bib"):
        log.info("Creating bibliography of source_folder {}".format(
            self.source_folder))
        log.info("Created bibliography in file {}".format(
            os.path.join(self.outdir, filename)))

        keys = []
        if self.bibtex_list is None:
            files = glob.glob(self.source_folder + "/*")
        else:
            files = []
            for bibtex in self.bibtex_list:
                files.append(os.path.join(self.source_folder, bibtex))

        combined_data = ""
        for file in files:
            with open(file, "r") as f:
                data = f.read()
                key = data.split("\n")[0]
                idx = key.find("{")
                key = key[idx + 1:-1]
                keys.append(key)
            combined_data += data + "\n"

        file_to_write = os.path.join(self.outdir, filename)
        with open(file_to_write, "w") as f:
            f.write(combined_data)
        self.keys = keys
        return self.keys

    def convert_latex_to_html(self):
        cwd = os.getcwd()
        os.chdir(self.outdir)
        copy_cmd = f"cp {self.convert_latex_to_html} ."
        os.system(copy_cmd)
        cmd = "{pandoc_command} --standalone --output {output} --citeproc --mathjax references.bib"
        cmd += " --from bibtex --csl {conversion_style_to_html}"
        cmd = cmd.format(
            pandoc_command=self.pandoc_command,
            output=self.filename.replace(".tex", ".html"),
            conversion_style_to_html=self.conversion_style_to_html)
        os.system(cmd)
        os.chdir(cwd)

    def extract_body_of_html(self):
        if not os.path.exists(self.html_file):
            raise FileNotFoundError(f"File {self.html_file} does not exist.")

        with open(self.html_file, "r") as f:
            html = f.read()
        soup = BeautifulSoup(html, features="html.parser")

        body = soup.find("body")
        return body

    def write_html_body_to_file(self):
        body = self.extract_body_of_html()
        with open(self.html_body_file, "w") as f:
            f.write(str(body))

    def copy_html_to_target(self, target):
        self.copy_file_to_target(source=self.html_file, target=target)

    def copy_html_body_to_target(self, target):
        self.copy_file_to_target(source=self.html_body_file, target=target)

    def copy_file_to_target(self, source, target):
        dirname = os.path.dirname(target)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        cmd = f"cp {source} {target}"
        os.system(cmd)
