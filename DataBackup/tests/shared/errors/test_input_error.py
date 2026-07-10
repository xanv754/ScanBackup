import unittest
from pathlib import Path
from unittest.mock import patch
from scanbackup.shared.errors.input_error import (
    FileEmptyError,
    FileExtensionError,
    ContentFileError,
    DataNotFoundError,
)


@patch("scanbackup.shared.errors.input_error.Terminal")
@patch("scanbackup.shared.errors.input_error.Log")
class TestInputError(unittest.TestCase):
    """Unit tests for the file input error hierarchy."""

    def test_file_empty_error_includes_filepath(self, mock_log, mock_terminal) -> None:
        """FileEmptyError must include the offending filepath in its message."""
        error = FileEmptyError("/tmp/empty.csv")
        self.assertIn("/tmp/empty.csv", str(error))

    def test_file_extension_error_includes_filepath(self, mock_log, mock_terminal) -> None:
        """FileExtensionError must include the offending filepath in its message."""
        error = FileExtensionError("/tmp/data.xls")
        self.assertIn("/tmp/data.xls", str(error))

    def test_content_file_error_default_message(self, mock_log, mock_terminal) -> None:
        """ContentFileError without a message must build a default one with the filepath."""
        error = ContentFileError("/tmp/data.csv")
        self.assertIn("/tmp/data.csv", str(error))

    def test_content_file_error_appends_wrapped_error(self, mock_log, mock_terminal) -> None:
        """ContentFileError must append the wrapped error text when provided."""
        error = ContentFileError("/tmp/data.csv", error=ValueError("boom"))
        self.assertIn("boom", str(error))

    def test_data_not_found_error_accepts_string_path(self, mock_log, mock_terminal) -> None:
        """DataNotFoundError must include a plain string filepath as-is."""
        error = DataNotFoundError("/tmp/missing")
        self.assertIn("/tmp/missing", str(error))

    def test_data_not_found_error_resolves_path_object(self, mock_log, mock_terminal) -> None:
        """DataNotFoundError must resolve a Path object to its absolute string form."""
        path = Path("relative/missing")
        error = DataNotFoundError(path)
        self.assertIn(str(path.resolve()), str(error))


if __name__ == "__main__":
    unittest.main()
