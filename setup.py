#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fo:
    long_description = fo.read()


def map_extras_require(dct: dict[str, list[str]]):
    res = dict()
    for f, l in dct.items():
        res[f] = [i for r in l for i in res.get(r.strip("[]"), [r])]
    
    return res


setup(
    name="Jani-Common",
    version="0.0.1",
    author="David Kyalo",
    description="A python development toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidkyalo/jani-common",
    project_urls={
        "Bug Tracker": "https://github.com/davidkyalo/jani-common/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_namespace_packages(include=["jani.common"]),
    include_package_data=True,
    python_requires="~=3.9",
    install_requires=["typing-extensions >=4.0.1"],
    extras_require=map_extras_require(
        {
            "json": ["orjson>=3.6.5"],
            "locale": ["Babel >=2.9.1"],
            "moment": ["arrow >=1.2.1"],
            "money": ["[locale]", "py-moneyed >=2.0"],
            "networks": ["pydantic[email]"],
            "phone": ["[locale]", "phonenumbers>=8.12.40"],
            "all": [
                "[json]",
                "[locale]",
                "[moment]",
                "[money]",
                "[networks]",
                "[phone]",
            ],
        }
    ),
)
