import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.bras import (
    BrasDefaultDownlink,
    BrasDefaultUplink,
    BrasSourceUpdater,
    IpBrasDefault,
    IpBrasSourceUpdater,
)
from scrapper_scanbackup.bras.model import BrasPageModel
from scrapper_scanbackup.model import IpSourceModel, SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting

SIDEBAR_HTML = """
<div class="sidebar">
  <ul role="menu">
    <li class="nav-item menu">
      <a>ABC-BRAS</a>
      <ul>
        <li>
          <p>UPLINK POR BRAS</p>
          <ul>
            <li><p>ABC-BRAS-01</p><a href="/graficas/abc-bras-01-uplink.html">ver</a></li>
          </ul>
        </li>
        <li>
          <p>DOWNLINK POR BRAS</p>
          <ul>
            <li><p>ABC-BRAS-01</p><a href="/graficas/abc-bras-01-downlink.html">ver</a></li>
          </ul>
        </li>
      </ul>
    </li>
    <li class="nav-item menu">
      <a>NOT-A-MATCH</a>
      <ul><li><p>x</p></li></ul>
    </li>
  </ul>
</div>
"""


class TestBrasSourceUpdater(unittest.TestCase):
    """Unit tests for the BrasSourceUpdater sidebar discovery logic."""

    def setUp(self) -> None:
        """Build the default BRAS layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="bras",
            url="https://scan.example.com/bras",
            type="",
            locked=False,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_get_default_pages_classifies_uplink_and_downlink(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should keep only BRAS-named menus and classify their pages as UPLINK or DOWNLINK."""
        mock_get_html.return_value = BeautifulSoup(SIDEBAR_HTML, "html.parser")

        pages = BrasSourceUpdater()._get_default_pages(self.info)

        self.assertEqual(len(pages), 2)
        self.assertEqual({page.type_link for page in pages}, {"UPLINK", "DOWNLINK"})
        self.assertTrue(all(page.name == "ABC-BRAS-01" for page in pages))

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_get_default_pages_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the sidebar page cannot be fetched."""
        mock_get_html.return_value = None

        pages = BrasSourceUpdater()._get_default_pages(self.info)

        self.assertEqual(pages, [])

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_scrapes_uplink_and_downlink_pages_for_untyped_entries(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should discover the BRAS pages and scrape both their uplink and downlink detail pages."""
        setting = MagicMock(spec=ScrapperSetting)
        setting.get_data_layer.return_value = [self.info]

        uplink_detail_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-01 10GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-01-up.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        downlink_detail_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-01 5GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-01-down.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(SIDEBAR_HTML, "html.parser"),
            BeautifulSoup(uplink_detail_html, "html.parser"),
            BeautifulSoup(downlink_detail_html, "html.parser"),
        ]

        sources = BrasSourceUpdater().execute(setting)

        self.assertEqual(len(sources), 2)
        self.assertEqual({source.model for source in sources}, {"UPLINK", "DOWNLINK"})

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_ignores_entries_with_a_declared_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore entries that declare a vendor type, since BRAS only has a default scrapper."""
        setting = MagicMock(spec=ScrapperSetting)
        typed_info = LayerModel(
            layer="bras", url="https://scan.example.com/bras", type="huawei", locked=False
        )
        setting.get_data_layer.return_value = [typed_info]

        sources = BrasSourceUpdater().execute(setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


class TestBrasDefaultUplink(unittest.TestCase):
    """Unit tests for the BrasDefaultUplink scrapper."""

    def setUp(self) -> None:
        """Build the BRAS layer info and target page shared by every test in this class."""
        self.info = LayerModel(
            layer="bras",
            url="https://scan.example.com/bras",
            type="",
            locked=False,
        )
        self.pages = [
            BrasPageModel(
                name="ABC-BRAS-01",
                url="https://scan.example.com/graficas/abc-bras-01-up.html",
                type_link="UPLINK",
            )
        ]

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn an uplink interface row into a SourceModel with capacity."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-01 10GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-01-real.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BrasDefaultUplink().scrapper(self.info, self.pages)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "ABC-BRAS-01 10GB")
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(sources[0].model, "UPLINK")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_skips_rows_without_the_traffic_suffix(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should discard rows that are not individual traffic interfaces."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Resumen General</li>
              <li id="graficas"><a href="/graficas/resumen.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BrasDefaultUplink().scrapper(self.info, self.pages)

        self.assertEqual(sources, [])

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_keeps_previous_pages_when_a_later_page_fails(
        self, mock_get_html: MagicMock
    ) -> None:
        """A failed fetch for one BRAS page must not discard sources already scraped from another."""
        pages = [
            BrasPageModel(
                name="ABC-BRAS-01",
                url="https://scan.example.com/graficas/abc-bras-01-up.html",
                type_link="UPLINK",
            ),
            BrasPageModel(
                name="ABC-BRAS-02",
                url="https://scan.example.com/graficas/abc-bras-02-up.html",
                type_link="UPLINK",
            ),
        ]
        first_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-01 10GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-01-real.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [BeautifulSoup(first_html, "html.parser"), None]

        sources = BrasDefaultUplink().scrapper(self.info, pages)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "ABC-BRAS-01 10GB")


class TestBrasDefaultDownlink(unittest.TestCase):
    """Unit tests for the BrasDefaultDownlink scrapper."""

    def setUp(self) -> None:
        """Build the BRAS layer info and target page shared by every test in this class."""
        self.info = LayerModel(
            layer="bras",
            url="https://scan.example.com/bras",
            type="",
            locked=False,
        )
        self.pages = [
            BrasPageModel(
                name="ABC-BRAS-01",
                url="https://scan.example.com/graficas/abc-bras-01-down.html",
                type_link="DOWNLINK",
            )
        ]

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a downlink interface row into a SourceModel with capacity."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-01 5GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-01-real.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = BrasDefaultDownlink().scrapper(self.info, self.pages)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "ABC-BRAS-01 5GB")
        self.assertEqual(sources[0].capacidad, 5)
        self.assertEqual(sources[0].model, "DOWNLINK")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_keeps_previous_pages_when_a_later_page_fails(
        self, mock_get_html: MagicMock
    ) -> None:
        """A failed fetch for one BRAS page must not discard sources already scraped from another."""
        pages = [
            BrasPageModel(
                name="ABC-BRAS-01",
                url="https://scan.example.com/graficas/abc-bras-01-down.html",
                type_link="DOWNLINK",
            ),
            BrasPageModel(
                name="ABC-BRAS-02",
                url="https://scan.example.com/graficas/abc-bras-02-down.html",
                type_link="DOWNLINK",
            ),
        ]
        second_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">ABC-BRAS-02 5GB - Trafico de Red</li>
              <li id="graficas"><a href="/graficas/abc-bras-02-real.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [None, BeautifulSoup(second_html, "html.parser")]

        sources = BrasDefaultDownlink().scrapper(self.info, pages)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "ABC-BRAS-02 5GB")


class TestIpBrasDefault(unittest.TestCase):
    """Unit tests for the IpBrasDefault scrapper."""

    def setUp(self) -> None:
        """Build the IP BRAS layer info shared by every test in this class."""
        self.info = LayerModel(
            layer="ip_bras",
            url="https://scan.example.com/ip-bras",
            type="",
            locked=True,
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn an IP row into an IpSourceModel keeping only the IP address."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">10.0.0.1 - Bras Prueba</li>
              <li id="graficas"><a href="/graficas/ip1.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = IpBrasDefault().scrapper(self.info)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], IpSourceModel)
        self.assertEqual(sources[0].enlace, "10.0.0.1")
        self.assertEqual(
            sources[0].link, "https://scan.example.com/graficas/ip1.log"
        )

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_skips_the_total_summary_row(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should discard the aggregated 'SUMATORIA TOTAL BRAS' row."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Sumatoria Total Bras</li>
              <li id="graficas"><a href="/graficas/suma.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = IpBrasDefault().scrapper(self.info)

        self.assertEqual(sources, [])

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_html_is_missing(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list when the page cannot be fetched."""
        mock_get_html.return_value = None

        sources = IpBrasDefault().scrapper(self.info)

        self.assertEqual(sources, [])


class TestIpBrasSourceUpdater(unittest.TestCase):
    """Unit tests for the IpBrasSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_processes_entries_without_a_declared_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should scrape IP BRAS entries that have no explicit vendor type set."""
        info = LayerModel(
            layer="ip_bras",
            url="https://scan.example.com/ip-bras",
            type="",
            locked=True,
        )
        self.setting.get_data_layer.return_value = [info]

        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">10.0.0.1 - Bras Prueba</li>
              <li id="graficas"><a href="/g/ip1.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = IpBrasSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].enlace, "10.0.0.1")
        self.setting.get_data_layer.assert_called_once_with("ip_bras")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_ignores_entries_with_a_declared_type(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should ignore entries that declare a vendor type, since IP BRAS only has a default scrapper."""
        typed_info = LayerModel(
            layer="ip_bras",
            url="https://scan.example.com/ip-bras",
            type="huawei",
            locked=True,
        )
        self.setting.get_data_layer.return_value = [typed_info]

        sources = IpBrasSourceUpdater().execute(self.setting)

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


if __name__ == "__main__":
    unittest.main()
