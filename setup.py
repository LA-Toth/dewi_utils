#!/usr/bin/env python3
#
# DEWI: a developer tool and framework
# Copyright (C) 2012-2018  Laszlo Attila Toth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys

if sys.hexversion < 0x03060000:
    raise RuntimeError("Required python version: 3.6 or newer (current: %s)" % sys.version)

try:
    from setuptools import setup, find_packages

except ImportError:
    from distutils.core import setup

setup(
    name="dewi",
    description="A toolchain and framework for everyday tasks",
    long_description=\
    """
    DEWI is started as a developer tool, but contains many different commands (small tools).

    DEWI can also use as a framework via its plugins - it's highly extensible.

    It contains commands for
    * syncing directory trees to local / remote location
    * manage photos to eliminate duplicates and sort them in year/year-month/year-month-day/FNAME.EXT form
    * edit files specified as filename:linenumber form
    * split Balabit's Zorp logs to one session per file
    * log into the Ubuntu (Linux) running bash on ubuntu on windows, to the same directory

    It also contains framework for
    * plugins (used by DEWI)
    * generic modules (to split task, and so on) with a Config - dict to store values; and emit messages
    * logparser: parse log files by modules based on the generic modules and emit messages
    """,
    license="LGPLv3",
    version="1.5",
    author="Laszlo Attila Toth",
    author_email="python-dewi@laszloattilatoth.me",
    maintainer="Laszlo Attila Toth",
    maintainer_email="python-dewi@laszloattilatoth.me",
    keywords='tool framework development synchronization',
    url="https://github.com/LA-Toth/dewi",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Filesystems',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    zip_safe=True,
    use_2to3=False,
    python_requires='>=3.6',
    packages=find_packages(exclude=['pylintcheckers', '*test*']) + ['dewi.tests'],
    entry_points={
        'console_scripts': [
            'dewi=dewi.__main__:main',
        ]
    },
    requires=[
        'Jinja2',
        'pyyaml',
        'watchdog',
    ]
)
