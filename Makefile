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

dist: clean
	@echo 'building pydba release'
	python setup.py develop
	python setup.py sdist --formats=gztar,zip
	pip install --upgrade pip
	pip install wheel
	python setup.py bdist_wheel --universal

register:
	@echo 'releasing pydba'
	python setup.py register

push_tags:
	@echo 'syncing tags'
	git push --tags

test: clean
	@echo 'running tests'
	python setup.py test
