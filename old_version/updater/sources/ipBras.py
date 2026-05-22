from unidecode import unidecode
from bs4 import BeautifulSoup
from scanbackup.model import Source
from scanbackup.updater.sources.scrapping import Scrapping


class IPBrasHuawei(Scrapping):
    _PREFFIX_JUNK_WORD = "SUMATORIA"
    _SUFFIX_JUNK_WORD = " - "
    _model = "HUAWEI"
    _domain = ".net"

    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)

    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        interfaces = html.find_all("ul", class_="list-group")
        link_base = self.get_url().split(self._domain)[0] + self._domain
        del interfaces[0]
        for interface in interfaces:
            link_graphic = (
                interface.find("li", {"id": "graficas"}).find("a").get("href")
            )
            link = link_graphic.replace(".html", ".log")
            name_interface = (
                interface.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
            )
            name_interface = unidecode(name_interface)
            name_interface = name_interface.split(self._PREFFIX_JUNK_WORD)
            if len(name_interface) > 1:
                name_interface = name_interface[1].strip()
            else:
                name_interface = name_interface[0].strip()
            name_interface = name_interface.split(self._SUFFIX_JUNK_WORD)
            name_interface = name_interface[0].strip()
            name_interface = name_interface.rstrip(" -")
            capacity = self.get_capacity(link_base + link_graphic, name_interface)
            source = Source(
                link=link_base + link,
                name=name_interface,
                capacity=capacity,
                model=self._model,
            )
            sources.append(source)
        return sources

    def get_capacity(self, url: str, interface: str) -> str:
        return "0"
