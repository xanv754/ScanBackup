from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class IXPSourceScrapping(SourceScrapping): #TODO: Implement

    def _get_list_services(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        """Scrapping the information to obtain a list of bras existing."""
        pass

    def _get_info_interfaces(self) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            pass
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Caching interfaces. {error}")
            return []

    def get_capacity(self, param: str) -> str:
        # TODO
        return self.with_capacity

    def get_sources(self) -> list[Source]:
        pass
