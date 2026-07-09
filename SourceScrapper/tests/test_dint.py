import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.dint import DintHuawei, DintSourceUpdater
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestDintHuawei(unittest.TestCase):
    """Unit tests for the DintHuawei scrapper."""

    def setUp(self) -> None:
        """Build the Huawei DINT layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="dint",
            url="https://scan.example.com/dint",
            type="huawei",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a DINT interface row into a SourceModel with a cleaned name and capacity."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distinternet 10GE 1/2/3 - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/distinternet.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DintHuawei().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "DISTINTERNET 10GE 1/2/3")
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(
            sources[0].link, "https://scan.example.com/graficas/distinternet.log"
        )
        self.assertEqual(sources[0].model, "HUAWEI")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_defaults_capacity_to_zero_when_not_found(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should default capacity to 0 when no digit+G pattern is present in the name."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distinternet Sin Capacidad - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/sin-capacidad.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DintHuawei().scrapper(self.info)

        self.assertEqual(sources[0].capacidad, 0)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = DintHuawei().scrapper(self.info)

        self.assertEqual(sources, [])


class TestDintSourceUpdater(unittest.TestCase):
    """Unit tests for the DintSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_aggregates_multiple_huawei_entries(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should merge the sources of every Huawei DINT entry declared in the config."""
        first_info = LayerModel(
            layer="dint", url="https://scan.example.com/d1", type="huawei", locked=False
        )
        second_info = LayerModel(
            layer="dint", url="https://scan.example.com/d2", type="huawei", locked=False
        )
        self.setting.get_data_layer.return_value = [first_info, second_info]

        first_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distinternet Uno 10GE - Tráfico de Red</li>
            <li id="graficas"><a href="/g/uno.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        second_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distinternet Dos 20GE - Tráfico de Red</li>
            <li id="graficas"><a href="/g/dos.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(first_html, "html.parser"),
            BeautifulSoup(second_html, "html.parser"),
        ]

        sources = DintSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 2)
        self.assertEqual({source.enlace for source in sources}, {"DISTINTERNET UNO 10GE", "DISTINTERNET DOS 20GE"})
        self.setting.get_data_layer.assert_called_once_with("dint")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_ignores_unsupported_vendor_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore entries whose vendor type has no DINT scrapper implemented."""
        unsupported_info = LayerModel(
            layer="dint", url="https://scan.example.com/x", type="cisco", locked=False
        )
        self.setting.get_data_layer.return_value = [unsupported_info]

        sources = DintSourceUpdater().execute(self.setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


if __name__ == "__main__":
    unittest.main()
