#!/usr/bin/env python3
#
# DEWI utils: Small utilities
# Copyright (C) 2012-2021  Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
# see <http://www.gnu.org/licenses/>.

import sys

if sys.hexversion < 0x03080000:
    raise RuntimeError("Required python version: 3.8 or newer (current: %s)" % sys.version)

try:
    from setuptools import setup, find_packages

except ImportError:
    from distutils.core import setup

setup(
    name="dewi_utils",
    description="A toolchain and framework for everyday tasks",
    license="LGPLv3",
    version="2.5.0",
    author="Laszlo Attila Toth",
    author_email="python-dewi@laszloattilatoth.me",
    maintainer="Laszlo Attila Toth",
    maintainer_email="python-dewi@laszloattilatoth.me",
    keywords='tool framework development synchronization',
    url="https://github.com/LA-Toth/dewi_utils",
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Filesystems',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    zip_safe=True,
    use_2to3=False,
    python_requires='>=3.8',
    packages=find_packages(exclude=['pylintcheckers', '*test*']),
    install_requires=[
        'dewi_core>=3.0.0',
        'Jinja2',
        'threadpool',
    ]
)
