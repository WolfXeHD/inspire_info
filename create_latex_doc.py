__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

from inspire_info import LatexCreator

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
    document_maker = LatexCreator(template=template,
                                  outdir="publication_latex",
                                  folder="publications_bibtex")
    document_maker.make_bibliography()
    document_maker.create_latex_doc(filename="publications.tex")
