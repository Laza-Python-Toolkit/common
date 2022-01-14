#!/usr/bin/env python

from setuptools import setup, find_namespace_packages
from pathlib import Path



setup(
    name="laza-common",
    version="0.0.2",
    author="David Kyalo",
    description="A python development toolkit",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/laza-toolkit/common",
    project_urls={
        "Bug Tracker": "https://github.com/laza-toolkit/common/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_namespace_packages(include='laza.common'),
    include_package_data=True,
    python_requires="~=3.9",
    install_requires=["typing-extensions ~=4.0.1"],
    extras_require={
        "json": ["orjson ~=3.6.5"],
        "locale": ["Babel"],
        "moment": ["arrow"],
        "money": ["laza-common[locale]", "py-moneyed ~=2.0"],
        "networks": ["pydantic[email]"],
        "phone": ["laza-common[locale]","phonenumbers ~=8.12.40"],
        "all": [
            "laza-common[json,locale,moment,money,networks,phone]",
        ],
    },
)
