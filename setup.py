#!/usr/bin/env python3
#
# DEWI utils: Small utilities
# Copyright 2012-2022  Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import sys

if sys.hexversion < 0x030a0000:
    raise RuntimeError("Required python version: 3.10 or newer (current: %s)" % sys.version)

from setuptools import setup, find_packages

setup(
    name="dewi_utils",
    description="A toolchain and framework for everyday tasks",
    license="Apache License, Version 2.0",
    license_files=('COPYING',),
    version="3.1.0",
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
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Filesystems',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    zip_safe=True,
    use_2to3=False,
    python_requires='>=3.10',
    packages=find_packages(exclude=['pylintcheckers', '*test*']),
    install_requires=[
        'dewi_core >=5.4.0, <6',
        'Jinja2',
    ]
)
