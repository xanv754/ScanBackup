import unittest
from unittest.mock import patch
from scanbackup.shared.errors.db_error import (
    DatabaseError,
    DataImportError,
    FileImportNotFoundError,
    DataContentError,
)


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestDbError(unittest.TestCase):
    """Unit tests for the database error hierarchy."""

    def test_database_error_default_message(self, mock_log, mock_terminal) -> None:
        """DatabaseError without a message must use the default text."""
        error = DatabaseError()
        self.assertIn("base de datos", str(error))

    def test_data_import_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """DataImportError must append the extra message when provided."""
        error = DataImportError(extra_msg="archivo corrupto")
        self.assertIn("archivo corrupto", str(error))

    def test_file_import_not_found_includes_filepath(self, mock_log, mock_terminal) -> None:
        """FileImportNotFoundError must include the missing filepath."""
        error = FileImportNotFoundError("/tmp/missing.csv")
        self.assertIn("/tmp/missing.csv", str(error))

    def test_data_content_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """DataContentError must append the extra message when provided."""
        error = DataContentError(extra_msg="línea 3 inválida")
        self.assertIn("línea 3 inválida", str(error))


if __name__ == "__main__":
    unittest.main()
