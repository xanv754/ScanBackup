from unidecode import unidecode
from bs4 import BeautifulSoup
from scanbackup.model import Source
from scanbackup.updater.sources.scrapping import Scrapping
from scanbackup.utils import log


class BordeHuawei(Scrapping):
    _PREFFIX_JUNK_WORD = "ENLACE INTERNACIONAL"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
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
            link_graphic = interface.find("li", {"id": "graficas"}).find("a").get("href")
            link = link_graphic.replace(".html", ".log")
            name_interface = interface.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
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
            FLAG = "GE"
            capacity = None
            
            if FLAG in interface:
                content = interface.split(" ")
                for word in content:
                    if FLAG in word: capacity = str(word.split(FLAG)[0])
            else:
                soup = self.get_html(url)
                if not soup: raise Exception()
                block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")
                content = block.get_text(strip=True).split(" ")
                for word in content:
                    try:
                        word = word.replace(",", ".")
                        capacity = int(round(float(word)))
                    except: continue
            if not capacity: capacity = "0"
            else: return str(capacity)
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"
        
        
class BordeCisco(Scrapping):
    _PREFFIX_JUNK_WORD = "ROUTER"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
    _model = "CISCO"
    _domain = ".net"
    
    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)
        
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        interfaces = html.find_all("ul", class_="list-group")
        link_base = self.get_url().split(self._domain)[0] + self._domain
        for interface in interfaces:
            link_graphic = interface.find("li", {"id": "graficas"}).find("a").get("href")
            link = link_graphic.replace(".html", ".log")
            name_interface = interface.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
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
            capacity = None
            soup = self.get_html(url)
            if not soup: raise Exception()
            block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")
            content = block.get_text(strip=True).split(" ")
            for word in content:
                try:
                    word = word.replace(",", ".")
                    capacity = int(round(float(word)))
                except: continue
            if not capacity: capacity = "0"
            else: return str(capacity)
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"
        

class BordeJuniper(Scrapping):
    _PREFFIX_JUNK_WORD = "ENLACE INTERNACIONAL"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
    _model = "JUNIPER"
    _domain = ".net"
    
    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)
        
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        interfaces = html.find_all("ul", class_="list-group")
        link_base = self.get_url().split(self._domain)[0] + self._domain
        del interfaces[0]
        for interface in interfaces:
            link_graphic = interface.find("li", {"id": "graficas"}).find("a").get("href")
            link = link_graphic.replace(".html", ".log")
            name_interface = interface.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
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
            FLAG = "GB"
            capacity = None
            
            if FLAG in interface:
                content = interface.split(" ")
                for word in content:
                    if FLAG in word: capacity = str(word.split(FLAG)[0])
            else:
                soup = self.get_html(url)
                if not soup: raise Exception()
                block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")
                content = block.get_text(strip=True).split(" ")
                for word in content:
                    try:
                        word = word.replace(",", ".")
                        capacity = int(round(float(word)))
                    except: continue
            if not capacity: capacity = "0"
            else: return str(capacity)
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"