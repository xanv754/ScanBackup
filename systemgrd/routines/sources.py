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
        """Define the base path."""
        url = self.config.scan_url_borde_huawei
        base = url.split(".net")[0]
        self.url_base = base + ".net"

    def get_html(self, url: str) -> BeautifulSoup | None:
        """Get the HTML of the page."""
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
    def get_capacity(self, param: str) -> str:
        """Get the capacity of an interface.
        
        :param param: The name or url of the interface.
        :type param: str
        """
        pass

    @abstractmethod  
    def get_sources(self) -> list[Source]:
        """Get a list of sources for each existing interface."""
        pass
        
    @abstractmethod
    def save_sources(self, sources: list[Source]) -> bool:
        """Save the sources in a file corresponding to their layer.
        
        :param sources: The list of sources to save.
        :type sources: list[Source]
        """
        pass
    

class BordeSourceScrapping(SourceScrapping):

    def _get_info_interfaces(self, soup: BeautifulSoup, model: str) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
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
        
    def _scrap_borde_huawei(self) -> list[Source]:
        """Scrapping the information to obtain the sources borde Huawei."""
        soup = self.get_html(self.config.scan_url_borde_huawei)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Borde Huawei.")
            return []
        return self._get_info_interfaces(soup, "HUAWEI")

    def _scrap_cisco(self) -> list[Source]:
        """Scrapping the information to obtain the sources borde Cisco."""
        soup = self.get_html(self.config.scan_url_borde_cisco)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Borde Cisco.")
            return []
        return self._get_info_interfaces(soup, "CISCO")
    
    def get_capacity(self, param: str):
        try:
            soup = self.get_html(param)
            if not soup: raise Exception("Failed to obtain HTML from source.")
            block = soup.find('span', class_="d-block mb-3").find_next('p').find_next('i')
            capacity = block.get_text(strip=True).split(": ")[1].split("Gb")[0].strip().replace(",", ".")
            capacity = str(int(round(float(capacity))))
            return capacity
        except Exception as error:
            log.error(f"Failed to obtain capacity from {param}. {error}")
            return "0"

    def get_sources(self):
        interfaces_hw = self._scrap_borde_huawei()
        interfaces_cisco = self._scrap_cisco()
        return interfaces_hw + interfaces_cisco
    
    def save_sources(self, sources):
        try:
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Borde_bk.txt"):
                os.remove(f"{DataPath.SCAN_SOURCES}/Borde_bk.txt")
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Borde.txt"):
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
        """Scrapping the information to obtain a list of bras existing."""
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
        """Scrapping the information to obtain the sources for each interface."""
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
        
    def get_capacity(self, param: str):
        try:
            name_split = param.split("_")
            for content in name_split:
                content = content.upper().strip()
                if "GB" in content:
                    content = content.replace("GB", "")
                    return content
            return "5"
        except Exception as error:
            log.error(f"Failed to obtain capacity from {param}. {error}")
            return "0"

    def get_sources(self):
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
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Bras.txt"):
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
        

class CachingSourceScrapping(SourceScrapping):

    def _get_list_services(self, soup: BeautifulSoup) -> list[str, str]:
        """Scrapping the information to obtain a list of bras existing."""
        services = []
        blocks = soup.find('div', class_="sidebar").find('nav', class_="mt-2").find('ul', class_="nav nav-pills nav-sidebar flex-column").find('li', class_="nav-item menu-open").find('ul', class_="nav nav-treeview").find_all('li', class_="nav-item")
        del blocks[0]
        for item in blocks:
            block = item.find('a', class_="nav-link")
            link = block.get('href')
            if link == "#": continue
            service = block.find('p').get_text(strip=True)
            service = service.replace("Suma", "").strip().upper()
            if "ALIANZA" in service: service = "FACEBOOK"
            services.append((service, link))
        return services

    def _get_info_interfaces(self) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            soup = self.get_html(self.config.scan_url_caching)
            if not soup: 
                log.error("Failed to obtain sources from SCAN Caching.")
                return []
            services = self._get_list_services(soup)
            for service in services:
                soup = self.get_html(f"{self.url_base}{service[1]}")
                if not soup: 
                    log.error(f"Failed to obtain info from SCAN Caching {service[0]}.")
                    continue
                blocks = soup.find('section', class_="content").find('div', class_="row").find('div', class_="col-md-12").find_all('div', class_="col-sm-12")
                for item in blocks:
                    name = item.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                    if not name or "Sumatoria" in name:
                        continue
                    name = name.split(" - ")[0].replace("Router ", "").replace(" ", "_").replace("/", "").replace("(", "").replace(")", "").replace("%", "").replace("|", "-")
                    capacity = self.get_capacity(name)
                    link_original = item.find('li', {'id': 'graficas'}).find('a').get('href')
                    link = link_original.replace(".html", ".log")
                    source = Source(link=link, name=name, capacity=capacity, model=service[0])
                    sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Caching interfaces. {error}")
            return []
        else:
            return sources

    def get_capacity(self, param: str): 
        # TODO
        return "PENDIENTE"

    def get_sources(self):
        return self._get_info_interfaces()

    def save_sources(self, sources: list[Source]):
        try:
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Caching_bk.txt"):
                os.remove(f"{DataPath.SCAN_SOURCES}/Caching_bk.txt")
            if os.path.exists(f"{DataPath.SCAN_SOURCES}/Caching.txt"):
                os.rename(f"{DataPath.SCAN_SOURCES}/Caching.txt", f"{DataPath.SCAN_SOURCES}/Caching_bk.txt")
            with open(f"{DataPath.SCAN_SOURCES}/Caching.txt", "w") as file:
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
    
    bras_scrapper = BrasSourceScrapping()
    bras_sources = bras_scrapper.get_sources()
    status_update = bras_scrapper.save_sources(bras_sources)
    if status_update: log.info("Sources from SCAN Bras updated.")
    else: log.error("Failed to update sources from SCAN Bras.")

    caching_scrapper = CachingSourceScrapping()
    caching_sources = caching_scrapper.get_sources()
    status_update = caching_scrapper.save_sources(caching_sources)
    if status_update: log.info("Sources from SCAN Caching updated.")
    else: log.error("Failed to update sources from SCAN Caching.")