import unittest
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.collector.recolector import recolector

MODULE = "scanbackup.application.cli.collector.recolector"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestRecolector(unittest.TestCase):
    """Unit tests for the recolector orchestration function."""

    @patch(f"{MODULE}.SCANScanner")
    def test_executes_all_layers_when_no_layer_given(
        self, mock_scanner_cls, mock_log, mock_terminal
    ) -> None:
        """Without a layer, the scanner must run execute_all()."""
        scanner = MagicMock()
        mock_scanner_cls.return_value = scanner

        recolector(date="2026-01-01")

        scanner.initialize.assert_called_once_with(date="2026-01-01")
        scanner.execute_all.assert_called_once()
        scanner.execute_layer.assert_not_called()

    @patch(f"{MODULE}.SCANScanner")
    def test_executes_a_single_layer_when_given(
        self, mock_scanner_cls, mock_log, mock_terminal
    ) -> None:
        """With a layer, the scanner must run execute_layer(layer) instead."""
        scanner = MagicMock()
        mock_scanner_cls.return_value = scanner

        recolector(layer="BORDE")

        scanner.execute_layer.assert_called_once_with("BORDE")
        scanner.execute_all.assert_not_called()

    @patch(f"{MODULE}.SCANScanner")
    def test_exits_with_code_1_on_scanner_failure(
        self, mock_scanner_cls, mock_log, mock_terminal
    ) -> None:
        """Any failure raised by the scanner must terminate the process with exit(1)."""
        mock_scanner_cls.return_value.initialize.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            recolector()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
