# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python3
RM      ?= rm
LINT    = flake8

#EXTRA_DIST=ipython/ipy_pydbgr.py pydbgr
PHONY=check clean dist distclean test test-unit test-functional rmChangeLog nosetests

#: Default target - same as "check"
all: check

#: Same as "check"
test: check

check:
	py.test pytest

#: Clean up temporary files
clean:
	@rm -fr */__pycache__/*.pyc
	$(PYTHON) ./setup.py $@

#: Create source (tarball) and binary (egg) distribution
dist:
	$(PYTHON) ./setup.py sdist bdist_egg

#: Create source tarball
sdist:
	$(PYTHON) ./setup.py sdist

#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint:
	$(LINT) trepan

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg


# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist

#: Remove ALL derived files
distclean: clean
	-rm -fr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name __pycache__ -exec rm -vr {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

#: Install package locally
verbose-install:
	$(PYTHON) ./setup.py install

#: Install package locally without the verbiage
install:
	$(PYTHON) ./setup.py install >/dev/null

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
