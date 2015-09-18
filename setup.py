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


with open('requirements.txt') as fp:
    install_requires = map(lambda x: x.strip(), fp.readlines())

setup(
    name="pydba",
    version='1.0.0',
    author='David P. D. Moss',
    author_email='drkjam@gmail.com',
    url='https://github.com/drkjam/pydba/',
    download_url='https://pypi.python.org/pypi/pydba/',
    license='MIT License',
    platforms='POSIX',
    packages=find_packages(),
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    install_requires=install_requires,
    description='Tools for DBAs (with deadlines)!',
    long_description="""`pydba` is provides a handy API to common database admin operations from Python.

API Usage
---------

Basic imports and class constructor usage.

    >>> from pydba import PostgresDB
    >>> db = PostgresDB()
    >>> db.available()
    True
    >>> db.names()
    ['postgres']

Database creation and deletion.

    >>> db.create('foo')
    >>> db.names()
    ['postgres', 'foo']
    >>> db.rename('foo', 'bar')
    >>> db.names()
    ['postgres', 'bar']

Database backup and restore.

    >>> db.dump('bar', 'bar.backup')
    >>> db.drop('bar')
    >>> db.names()
    ['postgres']
    >>> db.restore('bar', 'bar.backup')
    >>> db.names()
    ['postgres', 'bar']

Querying and removing shutting down database connections.

    >>> db.connections('postgres')
    [{'datname': 'postgres', 'state': 'idle', 'pid': 8937, 'psql', 'query': '', 'usename': 'drkjam', ...}]
    >>> db.kill_connections('postgres')
    >>> db.connections('postgres')
    []
""",
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
