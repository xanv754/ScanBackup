import unittest
from unittest.mock import MagicMock, patch
from scanbackup.shared.outputs.terminal import Terminal


class TestTerminal(unittest.TestCase):
    """Unit tests for the Terminal output helper."""

    def setUp(self) -> None:
        """Replace the shared rich Console with a mock to avoid real output."""
        self._console_patcher = patch.object(Terminal, "_console", MagicMock())
        self.mock_console = self._console_patcher.start()

    def tearDown(self) -> None:
        """Restore the original rich Console."""
        self._console_patcher.stop()

    def test_is_a_singleton(self) -> None:
        """Two instantiations must return the exact same object."""
        self.assertIs(Terminal(), Terminal())

    def test_info_includes_preffix(self) -> None:
        """info() must include the given preffix in the logged message."""
        Terminal.info(message="hola", preffix="MODULE")
        logged_message = self.mock_console.log.call_args[0][0]
        self.assertIn("MODULE", logged_message)
        self.assertIn("hola", logged_message)

    def test_warning_includes_preffix(self) -> None:
        """warning() must include the given preffix in the logged message."""
        Terminal.warning(message="cuidado", preffix="MODULE")
        logged_message = self.mock_console.log.call_args[0][0]
        self.assertIn("MODULE", logged_message)
        self.assertIn("WARNING", logged_message)

    def test_error_includes_preffix(self) -> None:
        """error() must include the given preffix in the logged message."""
        Terminal.error(message="fallo", preffix="MODULE")
        logged_message = self.mock_console.log.call_args[0][0]
        self.assertIn("MODULE", logged_message)
        self.assertIn("ERROR", logged_message)

    def test_info_without_preffix_omits_label(self) -> None:
        """info() without a preffix must not add the INFO label."""
        Terminal.info(message="hola")
        logged_message = self.mock_console.log.call_args[0][0]
        self.assertNotIn("INFO", logged_message)

    def test_loading_updates_status(self) -> None:
        """loading() must delegate the message update to the given status."""
        status = MagicMock()
        Terminal.loading(status, "procesando...")
        status.update.assert_called_once_with("procesando...")

    def test_list_prints_a_table(self) -> None:
        """list() must render a table through the shared console."""
        Terminal.list(["a", "b"], title="Items")
        self.mock_console.print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
