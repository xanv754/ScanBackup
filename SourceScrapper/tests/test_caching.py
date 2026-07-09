import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapper_scanbackup.caching import CachingHuawei, CachingSourceUpdater
from scrapper_scanbackup.caching.model import CachingPageModel
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class TestCachingHuawei(unittest.TestCase):
    """Unit tests for the CachingHuawei scrapper."""

    def setUp(self) -> None:
        """Build the Huawei CACHING layer info and a target service page for every test."""
        self.info = LayerModel(
            layer="caching",
            url="https://scan.example.com/caching",
            type="huawei",
            locked=False,
        )
        self.services = [
            CachingPageModel(
                name="NETFLIX", url="https://scan.example.com/caching/netflix.html"
            )
        ]

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_builds_source_from_html(self, mock_get_html: MagicMock) -> None:
        """It should turn a service interface row into a SourceModel named after the service."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Router Netflix Servidor 10GEB 1/2/3 - Tráfico de Red</li>
              <li id="graficas"><a href="/graficas/netflix-srv.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = CachingHuawei().scrapper(self.info, self.services)

        self.assertEqual(len(sources), 1)
        self.assertIsInstance(sources[0], SourceModel)
        self.assertEqual(sources[0].enlace, "NETFLIX SERVIDOR 10GEB 1/2/3")
        self.assertEqual(sources[0].capacidad, 10)
        self.assertEqual(sources[0].model, "NETFLIX")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_skips_summary_rows(self, mock_get_html: MagicMock) -> None:
        """It should discard rows that are totals instead of individual interfaces."""
        html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Sumatoria Netflix Total</li>
              <li id="graficas"><a href="/graficas/netflix-sum.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.return_value = BeautifulSoup(html, "html.parser")

        sources = CachingHuawei().scrapper(self.info, self.services)

        self.assertEqual(sources, [])

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_keeps_previous_services_when_a_later_page_fails(
        self, mock_get_html: MagicMock
    ) -> None:
        """A failed fetch for one service must not discard sources already scraped from another."""
        services = [
            CachingPageModel(
                name="NETFLIX", url="https://scan.example.com/caching/netflix.html"
            ),
            CachingPageModel(
                name="YOUTUBE", url="https://scan.example.com/caching/youtube.html"
            ),
        ]
        netflix_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Router Netflix Servidor 10GEB - Tráfico de Red</li>
              <li id="graficas"><a href="/graficas/netflix-srv.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [BeautifulSoup(netflix_html, "html.parser"), None]

        sources = CachingHuawei().scrapper(self.info, services)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].model, "NETFLIX")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_scrapper_returns_empty_list_when_no_services_are_given(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should return an empty list and never fetch any page when there are no services."""
        sources = CachingHuawei().scrapper(self.info, [])

        self.assertEqual(sources, [])
        mock_get_html.assert_not_called()


class TestCachingSourceUpdater(unittest.TestCase):
    """Unit tests for the CachingSourceUpdater orchestration class."""

    def setUp(self) -> None:
        """Build a mocked ScrapperSetting so tests do not depend on config.yml."""
        self.setting = MagicMock(spec=ScrapperSetting)

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_returns_sources_for_a_huawei_entry(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should discover the service pages from the sidebar and scrape each of them."""
        info = LayerModel(
            layer="caching",
            url="https://scan.example.com/caching",
            type="huawei",
            locked=False,
        )
        self.setting.get_data_layer.return_value = [info]

        sidebar_html = """
        <div class="sidebar">
          <ul role="menu">
            <ul class="nav nav-treeview">
              <li><p>Suma Netflix2</p><a href="/caching/netflix.html">ver</a></li>
            </ul>
          </ul>
        </div>
        """
        detail_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Router Netflix Servidor 10GEB - Tráfico de Red</li>
              <li id="graficas"><a href="/graficas/netflix-srv.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(sidebar_html, "html.parser"),
            BeautifulSoup(detail_html, "html.parser"),
        ]

        sources = CachingSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].model, "NETFLIX")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_keeps_other_entries_when_one_has_no_pages(
        self, mock_get_html: MagicMock
    ) -> None:
        """An entry whose sidebar cannot be read must not wipe out sources from other entries."""
        unreachable_info = LayerModel(
            layer="caching",
            url="https://scan.example.com/unreachable",
            type="huawei",
            locked=False,
        )
        working_info = LayerModel(
            layer="caching",
            url="https://scan.example.com/working",
            type="huawei",
            locked=False,
        )
        self.setting.get_data_layer.return_value = [unreachable_info, working_info]

        sidebar_html = """
        <div class="sidebar">
          <ul role="menu">
            <ul class="nav nav-treeview">
              <li><p>Suma Netflix2</p><a href="/caching/netflix.html">ver</a></li>
            </ul>
          </ul>
        </div>
        """
        detail_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Router Netflix Servidor 10GEB - Tráfico de Red</li>
              <li id="graficas"><a href="/graficas/netflix-srv.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [
            None,
            BeautifulSoup(sidebar_html, "html.parser"),
            BeautifulSoup(detail_html, "html.parser"),
        ]

        sources = CachingSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].model, "NETFLIX")

    @patch("scrapper_scanbackup.utils.Scrapper.get_html")
    def test_execute_matches_the_huawei_type_regardless_of_case(
        self, mock_get_html: MagicMock
    ) -> None:
        """It should recognize the Huawei type even if the config declares it with different casing."""
        info = LayerModel(
            layer="caching",
            url="https://scan.example.com/caching",
            type="Huawei",
            locked=False,
        )
        self.setting.get_data_layer.return_value = [info]

        sidebar_html = """
        <div class="sidebar">
          <ul role="menu">
            <ul class="nav nav-treeview">
              <li><p>Suma Netflix2</p><a href="/caching/netflix.html">ver</a></li>
            </ul>
          </ul>
        </div>
        """
        detail_html = """
        <section class="content"><div class="row"><div class="col-md-12">
          <div class="col-sm-12">
            <ul>
              <li id="subtitulo">Router Netflix Servidor 10GEB - Tráfico de Red</li>
              <li id="graficas"><a href="/graficas/netflix-srv.html">ver</a></li>
            </ul>
          </div>
        </div></div></section>
        """
        mock_get_html.side_effect = [
            BeautifulSoup(sidebar_html, "html.parser"),
            BeautifulSoup(detail_html, "html.parser"),
        ]

        sources = CachingSourceUpdater().execute(self.setting)

        self.assertEqual(len(sources), 1)


if __name__ == "__main__":
    unittest.main()
