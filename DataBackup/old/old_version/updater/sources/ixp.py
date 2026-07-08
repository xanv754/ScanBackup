import re
from unidecode import unidecode
from bs4 import BeautifulSoup
from scanbackup.model import Source
from scanbackup.updater.sources.scrapping import Scrapping
from scanbackup.utils import log


class IxpHuawei(Scrapping):
    _PREFFIX_JUNK_WORD = "ROUTER"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
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
            model = name_interface.split(" ")[-1]
            if model:
                model = re.sub(r"[-()\\]", " ", model)
            else:
                model = "IXP"
            capacity = self.get_capacity(link_base + link_graphic, name_interface)
            source = Source(
                link=link_base + link,
                name=name_interface,
                capacity=capacity,
                model=model,
            )
            sources.append(source)
        return sources

    def get_capacity(self, url: str, interface: str) -> str:
        try:
            FLAG = "GB"
            capacity = None
            if FLAG in interface:
                content = interface.split(" ")
                for word in content:
                    if FLAG in word:
                        word = re.sub(r"[-()\\]", " ", word)
                        capacity = str(word.split(FLAG)[0]).strip()
            if not capacity:
                capacity = "0"
            else:
                return str(capacity)
        except Exception as error:
            log.error(
                f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}"
            )
            return "0"
