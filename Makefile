#-----------------------------------------------------------------------------
#   Copyright (c) 2015, David P. D. Moss. All rights reserved.
#
#   Released under the MIT license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

SHELL = /bin/bash

.PHONY = all clean dist register push_tags test

all:
	@echo 'default target'

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf pydba.egg-info/
	find . -name '*.pyc' -exec rm -f {} ';'
	find . -name '*.pyo' -exec rm -f {} ';'

release_deps:
	@echo 'checking release dependencies'
	pip install --upgrade pip
	pip install wheel

register:
	@echo 'registering pydba'
	python setup.py register

dist: release_deps
	@echo 'building pydba distributions'
	python setup.py register
	python setup.py develop register sdist --formats=gztar,zip bdist_wheel --universal

release: clean release_deps
	@echo 'release pydba'
	python setup.py develop register sdist --formats=gztar,zip bdist_wheel --universal upload

push_tags:
	@echo 'syncing tags'
	git push --tags

test: clean
	@echo 'running tests'
	python setup.py test
