import re
from unidecode import unidecode
from bs4 import BeautifulSoup
from scanbackup.model import Source
from scanbackup.updater.sources.scrapping import Scrapping
from scanbackup.utils import log


class BrasHuawei(Scrapping):
    _UP_JUNK_WORD = "UPLINK POR BRAS"
    _DOWN_JUNK_WORD = "DOWNLINK POR BRAS"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
    _model_up = "UPLINK"
    _model_down = "DOWNLINK"
    _domain = ".net"

    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)

    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []

        def get_interfaces(
            page: BeautifulSoup, model: str, junk_word: str
        ) -> list[tuple[str, str]]:
            elements = []
            menu = (
                page.find("div", class_="sidebar")
                .find("nav")
                .find("ul", class_="nav nav-pills nav-sidebar flex-column")
                .find_all("li", class_="nav-item menu")
            )
            for level in menu:
                block = level.find("ul", class_="nav nav-treeview").find_all(
                    "li", class_="nav-item"
                )
                for item in block:
                    if item.find("p").get_text(strip=True) == junk_word:
                        all_bras = item.find("ul", class_="nav nav-treeview").find_all(
                            "li", class_="nav-item"
                        )
                        for bras in all_bras:
                            link = bras.find("a").get("href")
                            name = bras.find("p").get_text(strip=True)
                            elements.append((link, name, model))
            return elements

        interfaces_up = get_interfaces(
            page=html, model=self._model_up, junk_word=self._UP_JUNK_WORD
        )
        interfaces_down = get_interfaces(
            page=html, model=self._model_down, junk_word=self._DOWN_JUNK_WORD
        )
        interfaces = interfaces_up + interfaces_down
        link_base = self.get_url().split(self._domain)[0] + self._domain
        for bras in interfaces:
            soup = self.get_html(link_base + bras[0])
            if not soup:
                continue
            blocks = soup.find("section", class_="content").find_all(
                "div", class_="col-sm-12"
            )
            del blocks[0]
            for block in blocks:
                name_interface = (
                    block.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
                )
                name_interface = unidecode(name_interface)
                name_interface = name_interface.split(self._SUFFIX_JUNK_WORD)[0]
                name_interface = name_interface.rstrip(" -")
                link_graphic = (
                    block.find("li", {"id": "graficas"}).find("a").get("href")
                )
                capacity = self.get_capacity(link_base + link_graphic, name_interface)
                link = link_graphic.replace(".html", ".log")
                source = Source(
                    link=link_base + link,
                    name=name_interface,
                    capacity=capacity,
                    model=bras[2],
                )
                sources.append(source)
        return sources

    def get_capacity(self, url: str, interface: str) -> str:
        try:
            FLAG = "GB"
            capacity = None
            if FLAG in interface:
                interface = re.sub(r"[-()\\]", " ", interface)
                interface = re.sub(r"\s+", " ", interface).strip()
                interfaces = interface.split(" ")
                for word in interfaces:
                    if FLAG in word:
                        capacity = str(word.split(FLAG)[0])
            if not capacity:
                capacity = "5"
            return capacity
        except Exception as error:
            log.error(
                f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}"
            )
            return "0"
