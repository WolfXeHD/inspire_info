__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import argparse
import sys
from inspire_info import LatexCreator

def parse_args(args):
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

    return dict(vars(parser.parse_args(args)))

template = r"""\documentclass[11pt]{article}

\title{Multiple Bibliographies with \texttt{multibib}}
\author{Tim Wolf}
\date{}

\usepackage[resetlabels,labeled]{multibib}
\newcites{Math}{Math Readings}
\newcites{Phys}{Physics Readings}

\begin{document}

\maketitle

__NOCITES__

\bibliographystyle{unsrt}
\bibliography{references}

% \bibliographystyleMath{unsrt}
% \bibliographyMath{refs-etc}

% \bibliographystylePhys{unsrt}
% \bibliographyPhys{refs-etc}

\end{document}
"""


if __name__ == "__main__":
    parsed_args = parse_args(sys.argv[1:])
    document_maker = LatexCreator(template=template,
                                  outdir=parsed_args['output_dir'],
                                  source_folder=parsed_args["source_dir"])
    document_maker.make_bibliography()
    document_maker.create_latex_doc(filename="publications.tex")
