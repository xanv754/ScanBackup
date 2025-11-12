from unidecode import unidecode
from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import Scrapping
from systemgrd.utils import log


class RaiHuawei(Scrapping):
    _PREFFIX_JUNK_WORD = "ROUTER"
    _SUFFIX_JUNK_WORD = "TRAFICO"
    _model = "HUAWEI"
    _domain = ".net"
    
    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)
        
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        link_base = self.get_url().split(self._domain)[0] + self._domain
        blocks = html.find("section", {"id": "features"}).find("div", class_="container").find("div", class_="row").find_all("div", class_="col-sm-12")
        for item in blocks:
            link_graphic = item.find("li", {"id": "graficas"}).find("a").get("href")
            link = link_graphic.replace(".html", ".log")
            name_interface = item.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
            name_interface = unidecode(name_interface)
            name_interface = name_interface.split(self._PREFFIX_JUNK_WORD)
            if len(name_interface) > 1: name_interface = name_interface[1].strip()
            else: name_interface = name_interface[0].strip()
            name_interface = name_interface.split(self._SUFFIX_JUNK_WORD)
            name_interface = name_interface[0].strip()
            name_interface = name_interface.rstrip(' -')
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
        try:
            FLAG = "Mb"
            capacity = None
            
            soup = self.get_html(url)
            if soup: 
                block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")
                info = block.get_text(strip=True).split(": ")[1]
                capacity = float(info.split(" ")[0])
                unit = info.split(" ")[1]
                if capacity and unit:
                    if FLAG in unit.capitalize():
                        capacity = capacity / 1000
                    if 2 <= capacity <= 10:
                        capacity = 10.0
                    elif (capacity % 10) >= 5:
                        capacity = capacity + (10 - (capacity % 10))
                    capacity = str(float(capacity))
                    return capacity
            return "0"
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"
        
        
class RaiZte(Scrapping):
    _PREFFIX_JUNK_WORD = "ROUTER"
    _SUFFIX_JUNK_WORD = "TRAFICO"
    _model = "ZTE"
    _domain = ".net"
    
    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)
        
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        link_base = self.get_url().split(self._domain)[0] + self._domain
        blocks = html.find("section", {"id": "features"}).find("div", class_="container").find("div", class_="row").find_all("div", class_="col-sm-12")
        for item in blocks:
            link_graphic = item.find("li", {"id": "graficas"}).find("a").get("href")
            link = link_graphic.replace(".html", ".log")
            name_interface = item.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
            name_interface = unidecode(name_interface)
            name_interface = name_interface.split(self._PREFFIX_JUNK_WORD)
            if len(name_interface) > 1: name_interface = name_interface[1].strip()
            else: name_interface = name_interface[0].strip()
            name_interface = name_interface.split(self._SUFFIX_JUNK_WORD)
            name_interface = name_interface[0].strip()
            name_interface = name_interface.rstrip(' -')
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
        try:
            FLAG = "Mb"
            capacity = None
            
            soup = self.get_html(url)
            if soup: 
                block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")
                info = block.get_text(strip=True).split(": ")[1]
                capacity = float(info.split(" ")[0])
                unit = info.split(" ")[1]
                if capacity and unit:
                    if FLAG in unit.capitalize():
                        capacity = capacity / 1000
                    if 2 <= capacity <= 10:
                        capacity = 10.0
                    elif (capacity % 10) >= 5:
                        capacity = capacity + (10 - (capacity % 10))
                    capacity = str(float(capacity))
                    return capacity
            return "0"
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"