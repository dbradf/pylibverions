from unittest.mock import patch

import pytest

import pylibversion.version_util as under_test

NS = "pylibversion.version_util"


def ns(relative_name):  # pylint: disable=invalid-name
    """Return a full name from a name relative to the test module"s name space."""
    return NS + "." + relative_name


class TestVersionTupleToStr:
    def test_string_returned(self):
        version_tuple = (0, 1, 2)

        version_str = under_test.version_tuple_to_str(version_tuple)

        assert version_str == "0.1.2"


class TestLookupLatestVersionInPypi:
    @patch(ns("requests.get"))
    def test_pypi_data_is_returned(self, get_mock):
        version = "3.1.4"
        get_mock.return_value.json.return_value = {
            "info": {
                "version": version
            }
        }

        actual_version = under_test.lookup_latest_version_in_pypi("project_name")

        assert actual_version == version


class TestFindVersionLineInFile:
    def test_file_with_no_version(self, tmpdir):
        sample_file = tmpdir.join("sample.file")
        sample_file.write("hello world\n\nend of file\n")

        with pytest.raises(ValueError):
            under_test._find_version_line_in_file(sample_file)

    def test_file_with_multiple_versions(self, tmpdir):
        sample_file = tmpdir.join("sample.file")
        sample_file.write("VERSION = (0, 0, 1)\n\nVERSION = '0.0.1'\n")

        with pytest.raises(ValueError):
            under_test._find_version_line_in_file(sample_file)

    def test_file_with_one_version(self, tmpdir):
        sample_file = tmpdir.join("sample.file")
        sample_file.write("start\nVERSION = (3, 1, 4)\n\nhello world\n")

        version = under_test._find_version_line_in_file(sample_file)

        assert version == "VERSION = (3, 1, 4)\n"


class TestLookupLocalModuleVersion:
    def test_file_with_version(self, tmpdir):
        sample_file = tmpdir.join("__init__.py")
        sample_file.write("start\nVERSION = (3, 1, 4)\n\nhello world\n")

        version = under_test.lookup_local_module_version(sample_file.dirpath())

        assert version == "3.1.4"
