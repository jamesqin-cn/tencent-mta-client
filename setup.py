#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = "tencent-mta-client",
    version = "0.1.1",
    author = "jamesqin",
    author_email = "jamesqin@vip.qq.com",
    description = "tencent mta client is python sdk encapsulate for tencent mta api",
    long_description = long_description,
    long_description_content_type="text/markdown",
    license = "MIT",
    url = "https://github.com/jamesqin-cn/tencent-mta-client",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [
        'requests', 
        'tinyretry'
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
