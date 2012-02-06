#!/bin/sh

paver sdist upload

cd docs
make latex
cd _build/latex
pdflatex ecspy.tex
cd ../../..
rm -R html/_images/math
paver upload_docs --upload-dir html

