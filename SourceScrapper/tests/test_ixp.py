import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.ixp import IxpDefault, IxpSourceUpdater
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestIxpDefault(unittest.TestCase):
    """Unit tests for the IxpDefault scrapper."""

    def setUp(self) -> None:
        """Build the IXP layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="ixp",
            url="https://scan.example.com/ixp",
            type="",
            locked=False,
        )

    def _scrapper_with_row(self, subtitulo: str) -> list[SourceModel]:
        """Fetch a single-row IXP page through a mocked HTML response and return its sources."""
        html = f"""
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">{subtitulo}</li>
            <li id="graficas"><a href="/graficas/interfaz.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        with patch("scrapper_scanbackup.utils.Scrapper.get_html") as mock_get_html:
            mock_get_html.return_value = BeautifulSoup(html, "html.parser")
            return IxpDefault().scrapper(self.info)

    def test_scrapper_extracts_capacity_and_position_type(self) -> None:
        """It should extract the GB capacity and the type inside a POSICION-style name."""
        sources = self._scrapper_with_row("Puerto 10GB (Posicion A - Google)")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(sources[0].model, "GOOGLE")

    def test_scrapper_extracts_non_cantv_party_from_peering_privado(self) -> None:
        """It should return the non-CANTV party listed in a PEERING PRIVADO name."""
        sources = self._scrapper_with_row("Puerto (Peering Privado Cantv - Netflix)")

        self.assertEqual(sources[0].model, "NETFLIX")

    def test_scrapper_falls_back_to_the_dash_suffix_type(self) -> None:
        """It should use the text after the last dash when no known keyword is present."""
        sources = self._scrapper_with_row("Puerto (Local - Amazon)")

        self.assertEqual(sources[0].model, "AMAZON")

    def test_scrapper_defaults_type_to_ixp_when_unrecognized(self) -> None:
        """It should default the type to IXP when the name has no parenthesized type at all."""
        sources = self._scrapper_with_row("Puerto Sin Formato")

        self.assertEqual(sources[0].model, "IXP")
        self.assertEqual(sources[0].capacidad, 0)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = IxpDefault().scrapper(self.info)

        self.assertEqual(sources, [])


class TestIxpSourceUpdater(unittest.TestCase):
    """Unit tests for the IxpSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_processes_entries_without_a_declared_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should scrape IXP entries that have no explicit vendor type set."""
        info = LayerModel(
            layer="ixp", url="https://scan.example.com/ixp", type="", locked=False
        )
        self.setting.get_data_layer.return_value = [info]

        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Puerto 10GB (Posicion A - Google)</li>
            <li id="graficas"><a href="/g/google.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = IxpSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].model, "GOOGLE")
        self.setting.get_data_layer.assert_called_once_with("ixp")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_ignores_entries_with_a_declared_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore entries that declare a vendor type, since IXP only has a default scrapper."""
        info = LayerModel(
            layer="ixp", url="https://scan.example.com/ixp", type="cisco", locked=False
        )
        self.setting.get_data_layer.return_value = [info]

        sources = IxpSourceUpdater().execute(self.setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


if __name__ == "__main__":
    unittest.main()
