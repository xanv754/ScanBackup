from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class BordeSourceScrapping(SourceScrapping):

    def _get_info_interfaces(self, soup: BeautifulSoup, model: str) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            junk_word = "Enlace Internacional "
            interfaces = soup.find_all('ul', class_="list-group")
            del interfaces[0]
            for interface in interfaces:
                link_original = interface.find('li', {'id': 'graficas'}).find('a').get('href') # type: ignore
                link = link_original.replace(".html", ".log") # type: ignore
                name = interface.find('li', {'id': 'subtitulo'}).get_text(strip=True) # type: ignore
                preffix = name.split("-")[0].strip().split(junk_word)[1].strip() # type: ignore
                preffix = self.clear_name_format(preffix) # type: ignore
                suffix = name.split(" - ")[1].strip() # type: ignore
                suffix = self.clear_name_format(suffix) # type: ignore
                name = preffix + "_-_" + suffix
                capacity = self.get_capacity(self.url_base + "/" + link_original) # type: ignore
                source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=model)
                sources.append(source) # type: ignore
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Borde interfaces. {error}")
            return []
        else:
            return sources # type: ignore
        
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
    
    def get_capacity(self, param: str) -> str:
        try:
            soup = self.get_html(param)
            if not soup: raise Exception("Failed to obtain HTML from source.")
            block = soup.find('span', class_="d-block mb-3").find_next('p').find_next('i') # type: ignore
            capacity = block.get_text(strip=True).split(": ")[1].split("Gb")[0].strip().replace(",", ".") # type: ignore
            capacity = str(int(round(float(capacity))))
            return capacity
        except Exception as error:
            log.error(f"Failed to obtain capacity from {param}. {error}")
            return self.with_capacity

    def get_sources(self) -> list[Source]:
        self.set_url_base(self.config.scan_url_borde_huawei)
        interfaces_hw = self._scrap_borde_huawei()
        interfaces_cisco = self._scrap_cisco()
        return interfaces_hw + interfaces_cisco