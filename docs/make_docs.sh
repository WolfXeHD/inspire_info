#!/usr/bin/env bash
make clean
rm -r source/reference
sphinx-apidoc -o source/reference ../inspire-info
rm source/reference/modules.rst
make html
