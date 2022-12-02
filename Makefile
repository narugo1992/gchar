.PHONY: docs test unittest

PYTHON := $(shell which python)

PROJ_DIR      := .
DOC_DIR       := ${PROJ_DIR}/docs
BUILD_DIR     := ${PROJ_DIR}/build
DIST_DIR      := ${PROJ_DIR}/dist
TEST_DIR      := ${PROJ_DIR}/test
TESTFILE_DIR  := ${TEST_DIR}/testfile
SRC_DIR       := ${PROJ_DIR}/gchar
TEMPLATES_DIR := ${PROJ_DIR}/templates

RANGE_DIR      ?= .
RANGE_TEST_DIR := ${TEST_DIR}/${RANGE_DIR}
RANGE_SRC_DIR  := ${SRC_DIR}/${RANGE_DIR}

COV_TYPES ?= xml term-missing

package:
	$(PYTHON) -m build --sdist --wheel --outdir ${DIST_DIR}
clean:
	rm -rf ${DIST_DIR} ${BUILD_DIR} *.egg-info

test: unittest

unittest:
	pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},)

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod

# build test files
testfile:
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/7z_template-simple.7z) && \
		7z a -t7z $(abspath ${TESTFILE_DIR}/7z_template-simple.7z) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/rar_template-simple.rar) && \
		rar a $(abspath ${TESTFILE_DIR}/rar_template-simple.rar) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/zip_template-simple.zip) && \
		zip -r $(abspath ${TESTFILE_DIR}/zip_template-simple.zip) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/gztar_template-simple.tar.gz) && \
		tar -zcvf $(abspath ${TESTFILE_DIR}/gztar_template-simple.tar.gz) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/bztar_template-simple.tar.bz2) && \
		tar -cvjSf $(abspath ${TESTFILE_DIR}/bztar_template-simple.tar.bz2) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/xztar_template-simple.tar.xz) && \
		tar -cvJf $(abspath ${TESTFILE_DIR}/xztar_template-simple.tar.xz) * && \
		cd ../..
	cd ${TEMPLATES_DIR}/simple && \
		rm -rf $(abspath ${TESTFILE_DIR}/tar_template-simple.tar) && \
		tar -cvf $(abspath ${TESTFILE_DIR}/tar_template-simple.tar) * && \
		cd ../..
	cp "$(abspath ${TESTFILE_DIR}/gztar_template-simple.tar.gz)" "$(abspath ${TEMPLATES_DIR}/test/template/raw.tar.gz)"
	cp "$(abspath ${TESTFILE_DIR}/gztar_template-simple.tar.gz)" "$(abspath ${TEMPLATES_DIR}/test/template/.unpacked.tar.gz)"
