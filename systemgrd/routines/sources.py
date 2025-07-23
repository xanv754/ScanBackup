import os
import requests
from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pydantic import BaseModel
from urllib3.exceptions import InsecureRequestWarning
from systemgrd.constants import DataPath
from systemgrd.utils import log, ConfigurationHandler


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Source(BaseModel):
    """Model info of a source."""

    link: str
    name: str
    capacity: str
    model: str


class SourceScrapping(ABC):
    config: ConfigurationHandler
    url_base: str

    def __init__(self) -> None:
        self.config = ConfigurationHandler()
        self.set_url_base()

    def set_url_base(self) -> None:
        url = self.config.scan_url_borde_huawei
        base = url.split(".net")[0]
        self.url_base = base + ".net"

    def get_html(self, url: str) -> BeautifulSoup | None:
        try:
            html = requests.get(
                url, 
                verify=False, 
                auth=HTTPBasicAuth(self.config.scan_username, self.config.scan_password)
            )
            soup = BeautifulSoup(html.text, "html.parser")
        except Exception as error:
            log.error(f"Failed to obtain HTML from {url}. {error}")
            return None
        else:
            return soup

    @abstractmethod  
    def get_capacity(self, url: str) -> str:
        pass

    @abstractmethod  
    def get_sources(self) -> list[Source]:
        pass
        
    @abstractmethod
    def save_sources(self, sources: list[Source]) -> bool:
        pass
    

class BordeSourceScrapping(SourceScrapping):

    def _get_info_interfaces(self, soup: BeautifulSoup, model: str) -> list[Source]:
        try:
            sources = []
            interfaces = soup.find_all('ul', class_="list-group")
            del interfaces[0]
            for interface in interfaces:
                link_original = interface.find('li', {'id': 'graficas'}).find('a').get('href')
                link = link_original.replace(".html", ".log")
                name = interface.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                preffix = name.split("-")[0].strip().split("Enlace Internacional ")[1].strip()
                preffix = preffix.replace(" ", "_").replace("(", "").replace(")", "")
                suffix = name.split(" - ")[1].strip()
                suffix = suffix.replace(" ", "_").replace("/", "").replace("(", "").replace(")", "")
                name = preffix + "_-_" + suffix
                capacity = self.get_capacity(self.url_base + "/" + link_original)
                source = Source(link=link, name=name, capacity=capacity, model=model)
                sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Borde interfaces. {error}")
            return []
        else:
            return sources
        
    def _scrap_borde_huawei(self) -> list:
        soup = self.get_html(self.config.scan_url_borde_huawei)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Borde Huawei.")
            return []
        return self._get_info_interfaces(soup, "HUAWEI")

    def _scrap_cisco(self) -> list:
        soup = self.get_html(self.config.scan_url_borde_cisco)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Borde Cisco.")
            return []
        return self._get_info_interfaces(soup, "CISCO")
    
    def get_capacity(self, url: str) -> str:
        try:
            soup = self.get_html(url)
            if not soup: raise Exception("Failed to obtain HTML from source.")
            block = soup.find('span', class_="d-block mb-3").find_next('p').find_next('i')
            capacity = block.get_text(strip=True).split(": ")[1].split("Gb")[0].strip().replace(",", ".")
            capacity = str(int(round(float(capacity))))
            return capacity
        except Exception as error:
            log.error(f"Failed to obtain capacity from {url}. {error}")
            return "0"

    def get_sources(self) -> list[Source]:
        interfaces_hw = self._scrap_borde_huawei()
        interfaces_cisco = self._scrap_cisco()
        return interfaces_hw + interfaces_cisco
    
    def save_sources(self, sources) -> bool:
        try:
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Borde_bk.txt"):
                os.remove(f"{DataPath.SCAN_SOURCES}/Borde_bk.txt")
            os.rename(f"{DataPath.SCAN_SOURCES}/Borde.txt", f"{DataPath.SCAN_SOURCES}/Borde_bk.txt")
            with open(f"{DataPath.SCAN_SOURCES}/Borde.txt", "w") as file:
                for source in sources:
                    if source.capacity == "0": continue
                    file.write(f"{self.url_base}{source.link} {source.name} {source.capacity} {source.model}\n")
        except Exception as error:
            log.error(f"Failed to save sources. {error}")
            return False
        else:
            return True


class BrasSourceScrapping(SourceScrapping):

    def _get_list_bras(self, soup: BeautifulSoup, interface: str) -> list[str, str]:
        elements = []
        if interface == "UPLINK": content = "UPLINK POR BRAS"
        else: content = "DOWNLINK POR BRAS"
        menu = soup.find('div', class_="sidebar").find('nav').find('ul', class_='nav nav-pills nav-sidebar flex-column').find_all('li', class_="nav-item menu")
        for level in menu:
            block = level.find("ul", class_="nav nav-treeview").find_all('li', class_="nav-item")
            for item in block:
                if item.find('p').get_text(strip=True) == content:
                    all_bras = item.find('ul', class_="nav nav-treeview").find_all('li', class_="nav-item")
                    for bras in all_bras:
                        link = bras.find('a').get('href')
                        name = bras.find('p').get_text(strip=True)
                        elements.append((name, link))
        return elements

    def _get_info_interfaces(self, soup: BeautifulSoup, interface: str) -> list[Source]:
        try:
            sources = []
            list_bras = self._get_list_bras(soup, interface)
            for bras in list_bras:
                url_base = self.url_base.replace("11", "8")
                soup = self.get_html(url_base + bras[1])
                if not soup: 
                    log.error(f"Failed to obtain info from SCAN Bras {bras[0]}.")
                    continue
                blocks = soup.find('section', class_="content").find_all('div', class_="col-sm-12")
                del blocks[0]
                for block in blocks:
                    name = block.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                    preffix = name.split(" - ")[0].strip()
                    preffix = preffix.replace("/", "").replace("(", "").replace(")", "").replace(" ", "_").replace("%", "")
                    suffix = name.split(" - ")[1].strip()
                    suffix = suffix.replace("/", "").replace("(", "").replace(")", "").replace(" ", "_").replace("%", "")
                    name = preffix + "_-_" + suffix
                    link_original = block.find('li', {'id': 'graficas'}).find('a').get('href')
                    link = link_original.replace(".html", ".log")
                    capacity = self.get_capacity(name)
                    source = Source(link=link, name=name, capacity=capacity, model=interface)
                    sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Bras interfaces. {error}")
            return []
        else:
            return sources
        
    def get_capacity(self, name: str):
        try:
            name_split = name.split("_")
            for content in name_split:
                content = content.upper().strip()
                if "GB" in content:
                    content = content.replace("GB", "")
                    return content
            return "5"
        except Exception as error:
            log.error(f"Failed to obtain capacity from {name}. {error}")
            return "0"

    def get_sources(self) -> list[Source]:
        soup = self.get_html(self.config.scan_url_bras)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Bras.")
            return []
        sources_uplink = self._get_info_interfaces(soup, "UPLINK")
        sources_downlink = self._get_info_interfaces(soup, "DOWNLINK")
        return sources_uplink + sources_downlink

    def save_sources(self, sources):
        try:
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Bras_bk.txt"):
                os.remove(f"{DataPath.SCAN_SOURCES}/Bras_bk.txt")
            os.rename(f"{DataPath.SCAN_SOURCES}/Bras.txt", f"{DataPath.SCAN_SOURCES}/Bras_bk.txt")
            url_base = self.url_base.replace("11", "8")
            with open(f"{DataPath.SCAN_SOURCES}/Bras.txt", "w") as file:
                for source in sources:
                    if source.capacity == "0": continue
                    file.write(f"{url_base}{source.link} {source.name} {source.capacity} {source.model}\n")
        except Exception as error:
            log.error(f"Failed to save sources. {error}")
            return False
        else:
            return True

if __name__ == "__main__":
    borde_scrapper = BordeSourceScrapping()
    borde_sources = borde_scrapper.get_sources()
    status_update = borde_scrapper.save_sources(borde_sources)
    if status_update: log.info("Sources from SCAN Borde updated.")
    else: log.error("Failed to update sources from SCAN Borde.")
    
    bras_scrapper = BrasSourceScrapping()
    bras_sources = bras_scrapper.get_sources()
    status_update = bras_scrapper.save_sources(bras_sources)
    if status_update: log.info("Sources from SCAN Bras updated.")
    else: log.error("Failed to update sources from SCAN Bras.")