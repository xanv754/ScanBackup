import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.distr import DistHuawei, DistSourceUpdater
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestDistHuawei(unittest.TestCase):
    """Unit tests for the DistHuawei scrapper."""

    def setUp(self) -> None:
        """Build the Huawei DIST layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="dist",
            url="https://scan.example.com/dist",
            type="huawei",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a DIST interface row into a SourceModel with a cleaned name and capacity."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distri Prueba 10GE 1/2/3 - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/distri-prueba.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DistHuawei().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "DISTRI PRUEBA 10GE 1/2/3")
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(
            sources[0].link, "https://scan.example.com/graficas/distri-prueba.log"
        )
        self.assertEqual(sources[0].model, "HUAWEI")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_cleans_up_the_typo_traffic_suffix(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should also strip the '- TRAFICO DE RD' typo suffix seen on some DIST pages."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distri Prueba 5GE - Trafico de Rd</li>
            <li id="graficas"><a href="/graficas/distri-prueba.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DistHuawei().scrapper(self.info)

        self.assertEqual(sources[0].enlace, "DISTRI PRUEBA 5GE")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_defaults_capacity_to_zero_when_not_found(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should default capacity to 0 when no digit+G pattern is present in the name."""
        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distri Sin Capacidad - Tráfico de Red</li>
            <li id="graficas"><a href="/graficas/sin-capacidad.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DistHuawei().scrapper(self.info)

        self.assertEqual(sources[0].capacidad, 0)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = DistHuawei().scrapper(self.info)

        self.assertEqual(sources, [])


class TestDistSourceUpdater(unittest.TestCase):
    """Unit tests for the DistSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_returns_huawei_sources(self, mock_get_html: MagicMock) -> None:
        """It should fetch and return the sources for a Huawei DIST entry."""
        info = LayerModel(
            layer="dist", url="https://scan.example.com/dist", type="huawei", locked=False
        )
        self.setting.get_data_layer.return_value = [info]

        html = """
        <div id="main"><div class="row">
          <div><ul>
            <li id="subtitulo">Router Distri Prueba 10GE - Tráfico de Red</li>
            <li id="graficas"><a href="/g/distri.html">ver</a></li>
          </ul></div>
        </div></div>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = DistSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].model, "HUAWEI")
        self.setting.get_data_layer.assert_called_once_with("dist")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_ignores_unsupported_vendor_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore entries whose vendor type has no DIST scrapper implemented."""
        unsupported_info = LayerModel(
            layer="dist", url="https://scan.example.com/x", type="cisco", locked=False
        )
        self.setting.get_data_layer.return_value = [unsupported_info]

        sources = DistSourceUpdater().execute(self.setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


if __name__ == "__main__":
    unittest.main()
