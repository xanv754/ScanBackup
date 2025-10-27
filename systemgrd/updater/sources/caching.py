from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class CachingSourceScrapping(SourceScrapping):

    def _conditional_special_case(self, service: str) -> str:
        """Special case for some services."""
        if "ALIANZA" in service:
            return "FACEBOOK"
        else:
            return service

    def _get_list_services(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        """Scrapping the information to obtain a list of bras existing."""
        services = []
        blocks = soup.find("div", class_="sidebar").find("nav", class_="mt-2").find("ul", class_="nav nav-pills nav-sidebar flex-column").find("li", class_="nav-item menu-open").find("ul", class_="nav nav-treeview").find_all("li", class_="nav-item")  # type: ignore
        del blocks[0]
        for item in blocks:  # type: ignore
            block = item.find("a", class_="nav-link")  # type: ignore
            link = block.get("href")  # type: ignore
            if link == "#":
                continue
            service = block.find("p").get_text(strip=True)  # type: ignore
            service = service.replace("Suma", "").strip().upper()  # type: ignore
            service = self._conditional_special_case(service)  # type: ignore
            services.append((service, link))  # type: ignore
        return services  # type: ignore

    def _get_info_interfaces(self) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            junk_interface = "Sumatoria"
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
                blocks = soup.find("section", class_="content").find("div", class_="row").find("div", class_="col-md-12").find_all("div", class_="col-sm-12")  # type: ignore
                for item in blocks:  # type: ignore
                    name = item.find("li", {"id": "subtitulo"}).get_text(strip=True)  # type: ignore
                    if not name or junk_interface in name:
                        continue
                    name = name.split(" - ")[0].replace("Router ", "").replace(" ", "_").replace("/", "").replace("(", "").replace(")", "").replace("%", "").replace("|", "-")  # type: ignore
                    link_original = item.find("li", {"id": "graficas"}).find("a").get("href")  # type: ignore
                    capacity = self.get_capacity(f"{self.url_base}{link_original}")  # type: ignore
                    link = link_original.replace(".html", ".log")  # type: ignore
                    source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=service[0])  # type: ignore
                    sources.append(source)  # type: ignore
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Caching interfaces. {error}")
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
            capacity = round(float(capacity))
            if 5 <= capacity <= 10:
                capacity = 10
            elif (capacity % 10) > 5:
                capacity = capacity + (10 - (capacity % 10))
            elif (capacity % 10) <= 5:
                capacity = capacity + 1.5
            else:
                capacity = self.with_capacity
            capacity = str(float(capacity))
            return capacity
        except Exception as error:
            log.error(
                f"Failed to obtain capacity info from SCAN Caching interface ({param}) - {error}"
            )
            return self.with_capacity

    def get_sources(self) -> list[Source]:
        self.set_url_base(self.config.scan_url_caching)
        return self._get_info_interfaces()
