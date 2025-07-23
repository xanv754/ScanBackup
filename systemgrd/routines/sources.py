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
        if not soup: log.error("Failed to obtain sources from SCAN Borde Huawei.")
        return self._get_info_interfaces(soup, "HUAWEI")

    def _scrap_cisco(self) -> list:
        soup = self.get_html(self.config.scan_url_borde_cisco)
        if not soup: log.error("Failed to obtain sources from SCAN Borde Cisco.")
        return self._get_info_interfaces(soup, "CISCO")

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


if __name__ == "__main__":
    borde_scrapper = BordeSourceScrapping()
    borde_sources = borde_scrapper.get_sources()
    status_update = borde_scrapper.save_sources(borde_sources)
    if status_update: log.info("Sources from SCAN Borde updated.")
    else: log.error("Failed to update sources from SCAN Borde.")
    