#-----------------------------------------------------------------------------
#   Copyright (c) 2015, David P. D. Moss. All rights reserved.
#
#   Released under the MIT license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

SHELL = /bin/bash

.PHONY = all clean dist register push_tags test doc

all:
	@echo 'default target'

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf .eggs/
	rm -rf pydba.egg-info/
	find . -name '*.pyc' -exec rm -f {} ';'
	find . -name '*.pyo' -exec rm -f {} ';'
	find . -name '__pycache__' -exec rm -f {} ';'

realclean: clean
	rm -rf .cache/

release_deps:
	@echo 'checking release dependencies'
	pip install --upgrade pip
	pip install wheel

test: clean
	@echo 'running tests'
	python setup.py test

doc:
	@echo 'building docs'
	cp docs/source/intro.md README.md

dist: release_deps doc
	@echo 'building pydba distributions'
	python setup.py develop sdist --formats=gztar,zip bdist_wheel --universal

release: clean doc release_deps
	@echo 'release pydba'
	python setup.py develop register sdist --formats=gztar,zip bdist_wheel --universal upload

push_tags:
	@echo 'syncing tags'
	git push --tags
