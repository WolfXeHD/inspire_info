import os
import glob
import logging as log


class LatexCreator:
    def __init__(self, template, outdir, source_folder):
        self.template = template
        self.outdir = outdir
        self.source_folder = source_folder
        self.keys = None

        ensure_dirs(dirs=[self.outdir])

    def create_latex_doc(self, filename):
        create_latex_doc(template=self.template,
                         keys=self.keys,
                         filename=filename,
                         outdir=self.outdir)

    def make_bibliography(self, filename="references.bib"):
        log.info("Creating bibliography of source_folder {}".format(self.source_folder))
        self.keys = make_bibliography(source_folder=self.source_folder,
                                      outdir=self.outdir,
                                      filename=filename)
        log.info("Created bibliography in file {}".format(
            os.path.join(self.outdir, filename)))


def ensure_dirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def make_bibliography(source_folder, outdir, filename="references.bib"):
    keys = []
    files = glob.glob(source_folder + "/*")

    combined_data = ""
    for file in files:
        with open(file, "r") as f:
            data = f.read()
            key = data.split("\n")[0]
            idx = key.find("{")
            key = key[idx+1:-1]
            keys.append(key)
        combined_data += data + "\n"

    file_to_write = os.path.join(outdir, filename)
    with open(file_to_write, "w") as f:
        f.write(combined_data)

    return keys


def create_latex_doc(template, keys, filename, outdir):
    cwd = os.getcwd()
    os.chdir(outdir)
    nocite_string = ""
    for key in keys:
        nocite_string += r"\nocite{" + key + "}\n"
    this_template = template.replace("__NOCITES__", nocite_string)
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
