#!/usr/bin/env python
from setuptools import setup, find_packages

# long description with latest release notes
readme = open('README.rst').read()
news = open('NEWS.rst').read()
long_description = (readme + "\n\nLatest release notes\n====================\n"
                    + '\n'.join(news.split('\n\n\n', 1)[0].splitlines()[2:]))

# the actual setup
setup(name='gtabview', version='0.6',
      description='A simple graphical tabular data viewer',

      author="Yuri D'Elia",
      author_email="wavexx@thregr.org",
      license="MIT",
      long_description=long_description,
      url="https://github.com/wavexx/gtabview",
      keywords='data spreadsheet view viewer csv comma separated values',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Topic :: Office/Business :: Financial :: Spreadsheet',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Software Development :: User Interfaces',
                   'Topic :: Software Development :: Widget Sets',
                   'Topic :: Utilities'],

      scripts=['bin/gtabview'],
      packages=find_packages(),
      setup_requires=['setuptools', 'setuptools-git'],
      extras_require={'test': ['nose']},
      test_suite='nose.collector')
