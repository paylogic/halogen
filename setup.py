"""Setuptools entry point."""
import codecs
import os.path

import setuptools

# Get the version number from the code base.
from atilla import __version__ as atilla_version

tests_require = [
    "isodate",
    "mock",
    "pytest",
    "pytest-cov",
    "pytest-pep8",
    "pytest-pep257",
    "pytz",
]

long_description = []

for text_file in ['README.rst', 'CHANGES.rst']:
    with codecs.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), text_file), encoding='utf-8') as f:
        long_description.append(f.read())

install_requires = [
        "argparse>=1.2.1",
        "flask-script>=0.4.0",
        "flask>=0.10.1",
        "flask-cache",
        "halogen>=1.0.5",
        "python-memcached",
        "raven[flask]",
        "six",
        "Werkzeug>=0.9.3",
    ]

try:
    from collections import OrderedDict  # NOQA
except ImportError:  # pragma: no cover
    install_requires.append('ordereddict')

setuptools.setup(
    name='atilla',
    description="flask API projects helper",
    packages=setuptools.find_packages(include="atilla*"),
    long_description='\n'.join(long_description),
    author="Paylogic International and others",
    license="MIT license",
    author_email="developers@paylogic.com",
    url="https://github.com/paylogic/atilla",
    version=atilla_version,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ] + [("Programming Language :: Python :: %s" % x) for x in "2.7 3.4".split()],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
    }
)
