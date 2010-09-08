paver sdist
paver bdist_wininst
paver bdist_egg
cd docs
make latex
cd _build/latex
pdflatex ecspy.tex

