"""Setuptools entry point."""
import codecs
from os.path import abspath, dirname, join

from setuptools import setup

import halogen

long_description = []

for text_file in ["README.rst", "CHANGES.rst"]:
    with codecs.open(join(dirname(abspath(__file__)), text_file), encoding="utf-8") as f:
        long_description.append(f.read())

setup(
    name="halogen",
    description="Python HAL generation/parsing library",
    long_description="\n".join(long_description),
    author="Oleg Pidsadnyi, Paylogic International and others",
    license="MIT license",
    author_email="developers@paylogic.com",
    url="https://github.com/paylogic/halogen",
    version=halogen.__version__,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["halogen", "halogen.vnd"],
    install_requires=["cached-property", "isodate", "python-dateutil", "pytz", "six"],
    tests_require=["tox"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
