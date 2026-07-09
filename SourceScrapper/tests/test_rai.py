import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.rai import RaiHuawei, RaiSourceUpdater, RaiZte
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestRaiHuawei(unittest.TestCase):
    """Unit tests for the RaiHuawei scrapper."""

    def setUp(self) -> None:
        """Build the Huawei RAI layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="rai",
            url="https://scan.example.com/rai-huawei",
            type="huawei",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a dedicated-client interface row into a SourceModel with capacity."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Cliente Dedicado 5GE A/B/C - Trafico de Red</li>
            <li id="graficas"><a href="/graficas/cliente.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = RaiHuawei().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "CLIENTE DEDICADO 5GE A/B/C")
        self.assertEqual(sources[0].capacidad, 5)
        self.assertEqual(sources[0].model, "HUAWEI")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = RaiHuawei().scrapper(self.info)

        self.assertEqual(sources, [])


class TestRaiZte(unittest.TestCase):
    """Unit tests for the RaiZte scrapper."""

    def setUp(self) -> None:
        """Build the ZTE RAI layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="rai",
            url="https://scan.example.com/rai-zte",
            type="zte",
            locked=True,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a metro-ethernet interface row into a SourceModel with capacity."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Cliente Metroethernet 2GE X/Y - Trafico de Red</li>
            <li id="graficas"><a href="/graficas/metro.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = RaiZte().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "CLIENTE METROETHERNET 2GE X/Y")
        self.assertEqual(sources[0].capacidad, 2)
        self.assertEqual(sources[0].model, "ZTE")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = RaiZte().scrapper(self.info)

        self.assertEqual(sources, [])


class TestRaiSourceUpdater(unittest.TestCase):
    """Unit tests for the RaiSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_aggregates_huawei_and_zte_sources(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should dispatch each layer entry to its vendor scrapper and merge the results."""
        huawei_info = LayerModel(
            layer="rai", url="https://scan.example.com/h", type="huawei", locked=False
        )
        zte_info = LayerModel(
            layer="rai", url="https://scan.example.com/z", type="zte", locked=True
        )
        self.setting.get_data_layer.return_value = [huawei_info, zte_info]

        huawei_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Cliente Huawei 10GE - Trafico de Red</li>
            <li id="graficas"><a href="/g/huawei.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        zte_html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Cliente Zte 1GE - Trafico de Red</li>
            <li id="graficas"><a href="/g/zte.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(huawei_html, "html.parser"),
            BeautifulSoup(zte_html, "html.parser"),
        ]

        sources = RaiSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 2)
        self.assertEqual({source.model for source in sources}, {"HUAWEI", "ZTE"})
        self.setting.get_data_layer.assert_called_once_with("rai")


if __name__ == "__main__":
    unittest.main()
