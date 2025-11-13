import re
from unidecode import unidecode
from bs4 import BeautifulSoup
from scanbackup.model import Source
from scanbackup.updater.sources.scrapping import Scrapping
from scanbackup.utils import log


class CachingHuawei(Scrapping):
    _PREFFIX_JUNK_WORD = "ROUTER"
    _SUFFIX_JUNK_WORD = "TRAFICO DE RED"
    _SERVICE_SPECIAL = "ALIANZA"
    _SERVICE_SPECIAL_TRANSFORM = "FACEBOOK (META)"
    _domain = ".net"
    
    def __init__(self, url: str, layer: str, add_sources: bool = False) -> None:
        super().__init__(url, layer, add_sources)
        
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        sources = []
        JUNK_WORD = "SUMATORIA"
        def get_services(page: BeautifulSoup) -> list[tuple[str, str]]:
            JUNK_WORD = "Suma"
            services = []
            blocks = page.find("div", class_="sidebar").find("nav", class_="mt-2").find("ul", class_="nav nav-pills nav-sidebar flex-column").find("li", class_="nav-item menu-open").find("ul", class_="nav nav-treeview").find_all("li", class_="nav-item")
            del blocks[0]
            for item in blocks:
                block = item.find("a", class_="nav-link")
                link = block.get("href")
                if link == "#": continue
                service = block.find("p").get_text(strip=True)
                service = service.replace(JUNK_WORD, "").strip().upper()
                if self._SERVICE_SPECIAL in service: service = self._SERVICE_SPECIAL_TRANSFORM
                services.append((link, service))
            return services
        interfaces = get_services(html)
        link_base = self.get_url().split(self._domain)[0] + self._domain
        for interface in interfaces:
            link = interface[0]
            model = interface[1]
            page = self.get_html(link_base + link)
            if not page: continue
            blocks = page.find("section", class_="content").find("div", class_="row").find("div", class_="col-md-12").find_all("div", class_="col-sm-12")
            for item in blocks:
                name_interface = item.find("li", {"id": "subtitulo"}).get_text(strip=True).upper()
                if JUNK_WORD in name_interface: continue
                name_interface = unidecode(name_interface)
                name_interface = name_interface.split(self._PREFFIX_JUNK_WORD)
                if len(name_interface) > 1: name_interface = name_interface[1].strip()
                else: name_interface = name_interface[0].strip()
                name_interface = name_interface.split(self._SUFFIX_JUNK_WORD)[0]
                name_interface = name_interface.rstrip(' -')
                link_graphic = item.find("li", {"id": "graficas"}).find("a").get("href")
                capacity = self.get_capacity(link_base + link_graphic, name_interface)
                link = link_graphic.replace(".html", ".log")
                source = Source(
                    link=link_base + link, 
                    name=name_interface, 
                    capacity=capacity, 
                    model=model
                )
                sources.append(source)
        return sources
    
    def get_capacity(self, url: str, interface: str) -> str:
        try:
            FLAGS = ["G"]
            capacity = None
            
            interface = re.sub(r'[-()\\]', ' ', interface)
            interface = re.sub(r'\s+', ' ', interface).strip()
            interfaces = interface.split(" ")
            for word in interfaces:
                for FLAG in FLAGS:
                    if FLAG in word: 
                        try:
                            capacity = float(word[:-1])
                        except: continue
                        break
                if capacity: break
            if not capacity: return "0"
            return str(capacity)
        except Exception as error:
            log.error(f"Fallo al obtener la capacidad del enlace {interface} de la capa {self._layer} - {error}")
            return "0"