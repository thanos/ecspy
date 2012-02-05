paver sdist
paver bdist_wininst
paver bdist_egg
cd docs
COMMAND /C make latex
cd _build\latex
pdflatex ecspy.tex
cd ..\..\..

