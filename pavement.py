# Standard library
import os
import sys

# Set up Paver
import paver
import paver.doctools
import paver.misctasks
from paver.path import path
from paver.easy import *
import paver.setuputils
paver.setuputils.install_distutils_tasks()
try:
    from sphinxcontrib import paverutils
except:
    paverutils = None


PROJECT = 'ecspy'
VERSION = '0.1'

# The sphinx templates expect the VERSION in the shell environment
os.environ['VERSION'] = VERSION

# Read the long description to give to setup
README = path('README.txt').text()

# Scan the input for package information
# to grab any data files (text, images, etc.) 
# associated with sub-packages.
PACKAGE_DATA = paver.setuputils.find_package_data(PROJECT, 
                                                  package=PROJECT,
                                                  only_in_packages=True,
                                                  )

options(
    setup=Bunch(
        name = PROJECT,
        version = VERSION,
        description='A framework for creating evolutionary computations in Python.',
        long_description=README,
        author='Aaron Garrett',
        author_email='aaron.lee.garrett@gmail.com',
        url='http://%s.googlecode.com' % PROJECT,
        download_url = 'http://%s.googlecode.com/files/%s-%s.zip' % (PROJECT, PROJECT, VERSION),
        license='GPLv3+',
        platforms=('Any'),
        keywords=('python', 'optimization', 'evolutionary', 'computation', 'genetic', 'algorithm', 'particle', 'swarm'),

        classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ],
        
        # It seems wrong to have to list recursive packages explicitly.
        packages = [PROJECT],
        package_data=PACKAGE_DATA,
    ),
    
    sdist = Bunch(
    ),
    
    sphinx = Bunch(
        sourcedir='docs',
        docroot = '.',
        builder = 'html',
        doctrees='docs/_build/doctrees',
        confdir = 'docs',
    ),

    html = Bunch(
        builddir='docs',
        outdir='html',
        templates='pkg',
    ),

    # Some of the files include [[[ as part of a nested list data structure,
    # so change the tags cog looks for to something less likely to appear.
    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
#        includedir='PyMOTW',
    ),
)

# Stuff commonly used symbols into the builtins so we don't have to
# import them in all of the cog blocks where we want to use them.
# __builtins__['path'] = path

def remake_directories(*dirnames):
    """Remove the directories and recreate them.
    """
    for d in dirnames:
        d = path(d)
        if d.exists():
            d.rmtree()
        d.mkdir()
    return

@task
@needs(['cog'])
def html(options):
    if paverutils is None:
        raise RuntimeError('Could not find sphinxcontrib.paverutils, will not be able to build HTML output.')
    paverutils.html(options)
    return

@task
@needs(['generate_setup', 'minilib', 
        'html_clean', 
        'setuptools.command.sdist'
        ])
def sdist(options):
    """Create a source distribution.
    """
    return

@task
def html_clean(options):
    """Remove sphinx output directories before building the HTML.
    """
    remake_directories(options.sphinx.doctrees, options.html.outdir)
    html(options)
    return

