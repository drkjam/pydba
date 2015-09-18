from setuptools import setup, find_packages, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        import sys
        import subprocess

        saved_cwd = os.getcwd()
        try:
            os.chdir(os.path.join(os.path.dirname(__file__), 'tests'))
            errno = subprocess.call([sys.executable, '__init__.py'])
        finally:
            os.chdir(saved_cwd)
        raise SystemExit(errno)


setup(
    name="pydba",
    version="1.0.0",
    packages=find_packages(),

    author='David P. D. Moss',
    author_email='drkjam@gmail.com',

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
    cmdclass={'test': PyTest},

    description='Tools for DBAs (with deadlines)!',
    download_url='https://pypi.python.org/pypi/pydba/',
    keywords=[
        'Software Development',
        'Database Administration',
        'Systems Administration',
        'DBA',
        'PostgreSQL',
        'SQL',
    ],
    license='MIT License',
    long_description='',
    platforms='POSIX',
    url='',
)
