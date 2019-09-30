.PHONEY: clean unit_test unit_test_junit_export static_test static_test_junit_export test
.SILENT: clean

UNIT_TEST_TEST_SUITE   := all

TEST_REPORT_DIR        := Test_Reports

UNIT_TEST_REPORT_DIR   := $(TEST_REPORT_DIR)/unit_test
UNIT_TEST_JUNIT_DIR    := $(UNIT_TEST_REPORT_DIR)/junit
UNIT_TEST_COVERAGE_DIR := $(UNIT_TEST_REPORT_DIR)/coverage

STATIC_TEST_REPORT_DIR := $(TEST_REPORT_DIR)/static_test
STATIC_TEST_JUNIT_DIR  := $(STATIC_TEST_REPORT_DIR)/junit

TEST_TMP_FILES         := $(TEST_REPORT_DIR)/temporary_files


clean:
	-rm -r $(TEST_REPORT_DIR)

setup_reports:
	-mkdir -p $(TEST_REPORT_DIR)

	-mkdir -p $(UNIT_TEST_REPORT_DIR)
	-mkdir -p $(UNIT_TEST_JUNIT_DIR)
	-mkdir -p $(UNIT_TEST_COVERAGE_DIR)

	-mkdir -p $(STATIC_TEST_REPORT_DIR)
	-mkdir -p $(STATIC_TEST_JUNIT_DIR)

	-mkdir -p $(TEST_TMP_FILES)

static_test:
	@echo "1) flake8 (linter):"
	-flake8 vimba
	@echo

	@echo "2) mypy (static type checker):"
	-mypy vimba
	@echo

unit_test:
	coverage run Test/runner.py $(UNIT_TEST_TEST_SUITE) console
	coverage report -m
	-rm .coverage

test: unit_test static_test

static_test_junit_export:
	-flake8 vimba --output-file=$(TEST_TMP_FILES)/flake8.txt
	-flake8_junit $(TEST_TMP_FILES)/flake8.txt $(STATIC_TEST_JUNIT_DIR)/flake8_junit.xml

	-mypy vimba --junit-xml $(STATIC_TEST_JUNIT_DIR)/mypy_junit.xml

unit_test_junit_export:
	coverage run Test/runner.py $(UNIT_TEST_TEST_SUITE) junit_xml $(UNIT_TEST_JUNIT_DIR)
	coverage xml -o $(UNIT_TEST_COVERAGE_DIR)/coverage.xml
	coverage html -d $(UNIT_TEST_COVERAGE_DIR)/html

	-mv .coverage $(TEST_TMP_FILES)/coverage.txt

test_junit_export: clean setup_reports unit_test_junit_export static_test_junit_export
