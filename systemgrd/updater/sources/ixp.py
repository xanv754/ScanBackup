from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class IXPSourceScrapping(SourceScrapping):

    def _get_info_interfaces(self) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            soup = self.get_html(self.config.scan_url_ixp)
            if not soup:
                log.error("Failed to obtain sources from SCAN IXP.")
                return []
            print(soup)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN IXP interfaces. {error}")
            return []
        else:
            return sources  # type: ignore

    def get_capacity(self, param: str) -> str:
        try:
            soup = self.get_html(param)
            if not soup:
                raise Exception("Failed to obtain HTML from source.")
            block = soup.find("span", class_="d-block mb-3").find_next("p").find_next("i")  # type: ignore
            capacity = block.get_text(strip=True).split(": ")[1].split("Gb")[0].strip().replace(",", ".")  # type: ignore
            capacity = str(int(round(float(capacity))))
            return capacity
        except Exception as error:
            log.error(f"Failed to obtain capacity from {param}. {error}")
            return self.with_capacity

    def get_sources(self) -> list[Source]:
        self.set_url_base(self.config.scan_url_ixp)
        interfaces = self._get_info_interfaces()
        return interfaces


if __name__ == "__main__":
    updater = IXPSourceScrapping()
    response = updater.get_sources()
    print(response)
