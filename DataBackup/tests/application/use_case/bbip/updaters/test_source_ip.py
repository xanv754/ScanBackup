from unittest.mock import MagicMock, patch
from scanbackup.application.use_case.bbip.updaters.source_ip import (
    IPSourceUpdaterUseCase,
)
from scanbackup.domain import IPSourceBBIPEntity
from scanbackup.infrastructure import CSVWriter
from scanbackup.shared import CSVExportError
from tests.support import TempDirTestCase


class TestIPSourceUpdaterUseCase(TempDirTestCase):
    """Unit tests for the IPSourceUpdaterUseCase."""

    def setUp(self) -> None:
        """Build a use case instance backed by a mocked repository and reader."""
        super().setUp()
        self.repo = MagicMock()
        self.reader = MagicMock()
        self.use_case = IPSourceUpdaterUseCase(
            self.repo, self.tmp_dir, reader=self.reader, writer_factory=CSVWriter
        )

    def test_execute_upserts_and_discontinues_missing_sources(self) -> None:
        """execute() must upsert every parsed source and discontinue the rest."""
        source = MagicMock(interface="BRAS-00", layer="BRASIP")
        self.reader.import_data.return_value = [source]

        self.use_case.execute()

        self.repo.upsert_sources.assert_called_once_with([source])
        self.repo.discontinue_missing.assert_called_once_with(
            [{"interface": "BRAS-00", "layer": "BRASIP"}]
        )

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip")
    @patch("scanbackup.infrastructure.writers.csv.export.Configuration")
    def test_export_writes_one_csv_file_per_layer(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """export() must write a CSV file per requested layer using the repository data."""
        scanner = MagicMock()
        scanner.file_delimiter = ";"
        metadata = MagicMock()
        metadata.scanner = scanner
        mock_configuration.return_value.get_cfg_metadata.return_value = metadata
        mock_valid_layer.return_value = True

        entity = IPSourceBBIPEntity(
            link="http://example.com",
            interface="BRAS-00",
            layer="BRASIP",
        )
        self.repo.get_sources_by_layer.return_value = [entity]

        self.use_case.export(["brasip"])

        exported_file = self.tmp_dir / "BRASIP.csv"
        self.assertTrue(exported_file.exists())

    def test_export_continues_after_a_csv_export_error(self) -> None:
        """A CSVExportError for one layer must not stop the export of the others."""
        self.repo.get_sources_by_layer.side_effect = CSVExportError(filename="brasip")

        self.use_case.export(["brasip"])

        self.repo.get_sources_by_layer.assert_called_once()


if __name__ == "__main__":
    import unittest

    unittest.main()
