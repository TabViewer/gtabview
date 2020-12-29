#!/usr/bin/env python3
from setuptools import setup, find_packages
import gtabview_cli

# long description with latest release notes
readme = open('README.rst').read()
news = open('NEWS.rst').read()
long_description = (readme + "\n\nLatest release notes\n====================\n"
                    + '\n'.join(news.split('\n\n\n', 1)[0].splitlines()[2:]))

# the actual setup
setup(name='gtabview', version=gtabview_cli.__version__,
      description='A simple graphical tabular data viewer',

      author="Yuri D'Elia",
      author_email="wavexx@thregr.org",
      license="MIT",
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url="https://github.com/TabViewer/gtabview",
      keywords='data spreadsheet view viewer csv comma separated values',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Win32 (MS Windows)',
                   'Environment :: MacOS X',
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

      packages=find_packages(),
      setup_requires=['setuptools'],
      extras_require={'test': ['nose']},
      test_suite='nose.collector',
      entry_points={
          'console_scripts': [
              'gtabview=gtabview_cli.gtabview:main',
          ],
      },
      data_files=[('share/doc/gtabview', ['README.rst', 'NEWS.rst'])])
