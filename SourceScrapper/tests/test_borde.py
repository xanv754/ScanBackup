import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.borde import BordeCisco, BordeHuawei, BordeSourceUpdater
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestBordeCisco(unittest.TestCase):
    """Unit tests for the BordeCisco scrapper."""

    def setUp(self) -> None:
        """Build the Cisco BORDE layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="borde",
            url="https://scan.example.com/cisco",
            type="cisco",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a Cisco interface row into a SourceModel with a cleaned name and a .log link."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Enlace Prueba - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/enlace-prueba.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BordeCisco().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "ENLACE PRUEBA")
        self.assertEqual(
            sources[0].link, "https://scan.example.com/graficas/enlace-prueba.log"
        )
        self.assertEqual(sources[0].model, "CISCO")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = BordeCisco().scrapper(self.info)

        self.assertEqual(sources, [])


class TestBordeHuawei(unittest.TestCase):
    """Unit tests for the BordeHuawei scrapper."""

    def setUp(self) -> None:
        """Build the Huawei BORDE layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="borde",
            url="https://scan.example.com/huawei",
            type="huawei",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_extracts_capacity_and_name(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should keep international-link rows and extract the GE capacity from the name."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Enlace Internacional Telefonica 10GE X/Y/Z - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/telefonica.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BordeHuawei().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "TELEFONICA 10GE X/Y/Z")
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(sources[0].model, "HUAWEI")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_skips_rows_without_junk_word(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should discard rows that are not international-link summaries."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Sumatoria Total - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/sumatoria.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BordeHuawei().scrapper(self.info)

        self.assertEqual(sources, [])

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_defaults_capacity_to_zero_when_not_found(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should default capacity to 0 when no GE pattern is present in the name."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Enlace Internacional Sin Capacidad - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/sin-capacidad.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BordeHuawei().scrapper(self.info)

        self.assertEqual(sources[0].capacidad, 0)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = BordeHuawei().scrapper(self.info)

        self.assertEqual(sources, [])


class TestBordeSourceUpdater(unittest.TestCase):
    """Unit tests for the BordeSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_aggregates_cisco_and_huawei_sources(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should dispatch each layer entry to its vendor scrapper and merge the results."""
        cisco_info = LayerModel(
            layer="borde", url="https://scan.example.com/c", type="cisco", locked=False
        )
        huawei_info = LayerModel(
            layer="borde", url="https://scan.example.com/h", type="huawei", locked=False
        )
        self.setting.get_data_layer.return_value = [cisco_info, huawei_info]

        cisco_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Enlace Cisco - Trafico de Red</li>
            <li id="graficas"><a href="/g/cisco.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        huawei_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Enlace Internacional Huawei 10GE - Trafico de Red</li>
            <li id="graficas"><a href="/g/huawei.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(cisco_html, "html.parser"),
            BeautifulSoup(huawei_html, "html.parser"),
        ]

        sources = BordeSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 2)
        self.assertEqual({source.model for source in sources}, {"CISCO", "HUAWEI"})
        self.setting.get_data_layer.assert_called_once_with("borde")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_skips_unimplemented_juniper_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore Juniper entries without fetching any page, since that vendor is not implemented yet."""
        juniper_info = LayerModel(
            layer="borde", url="https://scan.example.com/j", type="juniper", locked=False
        )
        self.setting.get_data_layer.return_value = [juniper_info]

        sources = BordeSourceUpdater().execute(self.setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


if __name__ == "__main__":
    unittest.main()
