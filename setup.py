import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def _covert_markdown_badge(x, re_match_markdown=re.compile(r'^\[!\[[^]]+\]\(([^)]+)\)\]\((.+)\)$')):
    return re_match_markdown.sub(r'.. image:: \1\n  :target: \2', x)

#   Load external metadata.
with open('requirements.txt') as fp:
    install_requires = map(lambda x: x.strip(), fp.readlines())

with open('docs/source/intro.md') as fp:
    long_description = ''.join(map(_covert_markdown_badge, fp))

setup(
    name="pydba",
    version='1.2.0',
    author='David P. D. Moss',
    author_email='drkjam@gmail.com',
    url='https://github.com/drkjam/pydba/',
    download_url='https://pypi.python.org/pypi/pydba/',
    license='MIT License',
    platforms='POSIX',
    packages=find_packages(),
    cmdclass={'test': PyTest},
    tests_require=['pytest>=2.8'],
    install_requires=install_requires,
    description='Python tools for DBAs with deadlines!',
    long_description=long_description,
    keywords=[
        'Software Development',
        'Database Administration',
        'Systems Administration',
        'DBA',
        'PostgreSQL',
        'SQL',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: SQL',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: System',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Recovery Tools',
        'Topic :: System :: Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: System Shells',
        'Topic :: Utilities',
    ],
)
