#!/usr/bin/env python3
#
# DEWI: a developer tool and framework
# Copyright (C) 2012-2015  Laszlo Attila Toth
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
if sys.hexversion < 0x03040000:
    raise RuntimeError("Required python version: 3.4 or newer (current: %s)" % sys.version)

try:
    from setuptools import setup, find_packages

except ImportError:
    from distutils.core import setup

setup(
    name="dewi",
    description="A developer tool and framework to support everyday development including large projects",
    long_description=\
    """
    DEWI is a developer tool, bunch of commands, to support everyday development. This means
    very small comamnds, such as wrap vim to parse file.txt:123-like lines to check out, make,
    etc. a large project which has source code even in dozen of repositories.

    DEWI can also use as a framework via its plugins - it's highly extensible.

    The first versions are for finalize this framework and add some useful command.
    """,
    license="GPLv3",
    version="0.1",
    author="Laszlo Attila Toth",
    author_email="laszlo.attila.toth@gmail.com",
    maintainer="Laszlo Attila Toth",
    maintainer_email="laszlo.attila.toth.com",
    keywords='tool framework development',
    url="https://github.com/LA-Toth/dwa",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Documentation :: Sphinx',
    ],
    zip_safe=True,
    use_2to3=False,
    packages=find_packages(exclude=['pylintcheckers', '*test*']) + ['dewi.tests'],
    entry_points={
        'console_scripts': [
            'dewi=dewi.__main__:main',
        ]
    },
    requires=[
    ]
)
