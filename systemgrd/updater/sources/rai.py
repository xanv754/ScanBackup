from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class RAISourceScrapping(SourceScrapping):

    def _get_info_interfaces(self, soup: BeautifulSoup) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            model = "DEDICADO"
            blocks = soup.find('section', {'id': 'features'}).find('div', class_="container").find('div', class_="row").find_all('div', class_="col-sm-12") # type: ignore
            for item in blocks: # type: ignore
                link_original = item.find('li', {'id': 'graficas'}).find('a').get('href') # type: ignore
                link = link_original.replace(".html", ".log") # type: ignore
                name = item.find('li', {'id': 'subtitulo'}).get_text(strip=True) # type: ignore
                name = name.split(" ") # type: ignore
                del name[0]
                name = " ".join(name) # type: ignore
                name = name.split(" - ")[0]
                name = name.replace("/", "").replace("(", "").replace(")", "").replace("%", "").replace("|", "-").replace(" ", "_")
                capacity = self.get_capacity(link_original) # type: ignore
                source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=model)
                sources.append(source) # type: ignore
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Rai interfaces. {error}")
            return []
        else:
            return sources # type: ignore
        
    def _scrap_rai_hw(self) -> list[Source]:
        """Scrapping the information to obtain the sources Rai Huawei."""
        self.set_url_base(self.config.scan_url_rai_hw)
        soup = self.get_html(self.config.scan_url_rai_hw)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Rai Huawei.")
            return []
        return self._get_info_interfaces(soup)

    def _scrap_rai_zte(self) -> list[Source]:
        """Scrapping the information to obtain the sources Rai ZTE."""
        self.set_url_base(self.config.scan_url_rai_zte)
        soup = self.get_html(self.config.scan_url_rai_zte)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Rai ZTE.")
            return []
        return self._get_info_interfaces(soup)

    def get_capacity(self, param: str) -> str: 
        # TODO
        return self.with_capacity

    def get_sources(self) -> list[Source]:
        try:
            sources_hw = self._scrap_rai_hw()
            sources_zte = self._scrap_rai_zte()
            return sources_hw + sources_zte
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Rai interfaces. {error}")
            return []