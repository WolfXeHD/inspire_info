#!/bin/bash
make clean
rm -r source/reference
sphinx-apidoc -o source/reference ../inspire_info
rm source/reference/modules.rst
make html
