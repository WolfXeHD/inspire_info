#!/usr/bin/env python

__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.1.14'
__license__ = 'MIT'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
from inspire_info import LatexCreator


def parse_args():
    parser = argparse.ArgumentParser(
        description='Command line tool to search for authors in inspire')
    parser.add_argument('--source_dir',
                        type=str,
                        help="Directory where the bibtex-output is stored.",
                        default="bibtex"
                        )
    parser.add_argument('--output_dir',
                        type=str,
                        help="Directory where the latex-output is stored.",
                        required=True
                        )
    parser.add_argument('--filename',
                        type=str,
                        help="Filename of the latex-output.",
                        default="publications.tex"
                        )

    return dict(vars(parser.parse_args()))


template = r"""\documentclass[11pt]{article}

\title{Bibliography}
\author{Your friendly inspire_info}
\date{}

%\ usepackage[resetlabels,labeled]{multibib}
% \usepackage{bibtex}
% \newcites{Math}{Math Readings}
% \newcites{Phys}{Physics Readings}


\begin{document}

% \maketitle

__NOCITES__

\bibliographystyle{unsrt}
\bibliography{references}

% \bibliographystyleMath{unsrt}
% \bibliographyMath{refs-etc}

% \bibliographystylePhys{unsrt}
% \bibliographyPhys{refs-etc}

\end{document}
"""


def create_latex_doc(latex_template, output_dir, source_dir, filename):
    document_maker = LatexCreator(template=latex_template,
                                  outdir=output_dir,
                                  source_folder=source_dir,
                                  filename=filename)
    document_maker.make_bibliography()

    document_maker.create_latex_doc()


def main():
    parsed_args = parse_args()
    parsed_args["template"] = template
    create_latex_doc(**parsed_args)


if __name__ == "__main__":
    main()
