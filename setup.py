"""Setuptools entry point."""
import codecs
import sys
from os.path import abspath, dirname, join

from setuptools import setup
from setuptools.command.test import test as TestCommand

import halogen

install_requires = [
    'isodate',
    'pytz',
    'six',
]

try:
    from collections import OrderedDict  # noqa
except ImportError:  # pragma: no cover
    install_requires.append('ordereddict')


class ToxTestCommand(TestCommand):

    """Test command which runs tox under the hood."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        """Initialize options and set their defaults."""
        TestCommand.initialize_options(self)
        self.tox_args = '--recreate'

    def finalize_options(self):
        """Add options to the test runner (tox)."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Invoke the test runner (tox)."""
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

long_description = []

for text_file in ['README.rst', 'CHANGES.rst']:
    with codecs.open(join(dirname(abspath(__file__)), text_file), encoding='utf-8') as f:
        long_description.append(f.read())

setup(
    name="halogen",
    description="Python HAL generation/parsing library",
    long_description='\n'.join(long_description),
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
        "Programming Language :: Python :: 3"
    ] + [("Programming Language :: Python :: %s" % x) for x in "2.6 2.7 3.4".split()],
    cmdclass={"test": ToxTestCommand},
    packages=["halogen"],
    install_requires=install_requires,
    tests_require=["tox"],
)
