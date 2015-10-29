# -*- coding: utf-8 -*-
# Copyright (C) 2015 Richard Hughes <richard@hughsie.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA

from setuptools import setup

import sys
import os

f = open('README.md')
long_description = f.read().strip()
f.close()

requires = [
    # Nothing!
]

version = '0.5'

setup(
    name='python-appstream',
    version=version,
    description="Parse AppStream files when you don't have libappstream-glib",
    long_description=long_description,
    author='Richard Hughes',
    author_email='richard@hughsie.com',
    maintainer='Ralph Bean',
    maintainer_email='rbean@redhat.com',
    url='http://github.com/hughsie/python-appstream',
    license='LGPLv2+',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    install_requires=requires,
    packages=['appstream'],
    include_package_data=True,
    zip_safe=False,
)
