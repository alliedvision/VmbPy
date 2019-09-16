.PHONEY: clean unit_test unit_test_junit_export static_test static_test_junit_export test
.SILENT: clean

UNIT_TEST_REPORT_DIR   := Test_Reports/unit_test/junit
STATIC_TEST_REPORT_DIR := Test_Reports/static_test/junit

clean:
	-rm -r Test_Reports

static_test:
	@echo "Running static tests:"

	@echo "1) flake8 (linter):"
	-flake8 vimba
	@echo

	@echo "2) mypy (static type checker):"
	-mypy vimba
	@echo


unit_test:
	@echo "Running unit tests:"
	python -m unittest discover -s Test -p *_test.py


test: unit_test static_test


static_test_junit_export:
	-mkdir -p $(STATIC_TEST_REPORT_DIR)

	-flake8 vimba --output-file=$(STATIC_TEST_REPORT_DIR)/flake8.txt
	flake8_junit $(STATIC_TEST_REPORT_DIR)/flake8.txt $(STATIC_TEST_REPORT_DIR)/flake8_junit.xml

	-mypy vimba --junit-xml $(STATIC_TEST_REPORT_DIR)/mypy_junit.xml
	-rm $(STATIC_TEST_REPORT_DIR)/flake8.txt


unit_test_junit_export:
	mkdir -p $(UNIT_TEST_REPORT_DIR)
	python -m xmlrunner discover -s Test -p *_test.py -o $(UNIT_TEST_REPORT_DIR)


test_junit_export: clean unit_test_junit_export static_test_junit_export
