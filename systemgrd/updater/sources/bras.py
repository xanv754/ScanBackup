from bs4 import BeautifulSoup
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class BrasSourceScrapping(SourceScrapping):

    def _get_list_bras(
        self, soup: BeautifulSoup, uplink: bool
    ) -> list[tuple[str, str]]:
        """Scrapping the information to obtain a list of bras existing."""
        elements = []
        if uplink:
            content = "UPLINK POR BRAS"
        else:
            content = "DOWNLINK POR BRAS"
        menu = soup.find("div", class_="sidebar").find("nav").find("ul", class_="nav nav-pills nav-sidebar flex-column").find_all("li", class_="nav-item menu")  # type: ignore
        for level in menu:  # type: ignore
            block = level.find("ul", class_="nav nav-treeview").find_all("li", class_="nav-item")  # type: ignore
            for item in block:  # type: ignore
                if item.find("p").get_text(strip=True) == content:  # type: ignore
                    all_bras = item.find("ul", class_="nav nav-treeview").find_all("li", class_="nav-item")  # type: ignore
                    for bras in all_bras:  # type: ignore
                        link = bras.find("a").get("href")  # type: ignore
                        name = bras.find("p").get_text(strip=True)  # type: ignore
                        elements.append((name, link))  # type: ignore
        return elements  # type: ignore

    def _get_info_interfaces(self, soup: BeautifulSoup, uplink: bool) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            list_bras = self._get_list_bras(soup, uplink=uplink)
            for bras in list_bras:
                soup = self.get_html(self.url_base + bras[1])  # type: ignore
                if not soup:
                    log.error(f"Failed to obtain info from SCAN Bras {bras[0]}.")
                    continue
                blocks = soup.find("section", class_="content").find_all("div", class_="col-sm-12")  # type: ignore
                del blocks[0]
                for block in blocks:  # type: ignore
                    name = block.find("li", {"id": "subtitulo"}).get_text(strip=True)  # type: ignore
                    preffix = name.split(" - ")[0].strip()  # type: ignore
                    preffix = self.clear_name_format(preffix)  # type: ignore
                    suffix = name.split(" - ")[1].strip()  # type: ignore
                    suffix = self.clear_name_format(suffix)  # type: ignore
                    name = preffix + "_-_" + suffix
                    link_original = block.find("li", {"id": "graficas"}).find("a").get("href")  # type: ignore
                    link = link_original.replace(".html", ".log")  # type: ignore
                    capacity = self.get_capacity(name)
                    if uplink:
                        model = "UPLINK"
                    else:
                        model = "DOWNLINK"
                    source = Source(
                        link=f"{self.url_base}{link}",
                        name=name,
                        capacity=capacity,
                        model=model,
                    )
                    sources.append(source)  # type: ignore
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Bras interfaces. {error}")
            return []
        else:
            return sources  # type: ignore

    def get_capacity(self, param: str) -> str:
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
            return self.with_capacity

    def get_sources(self) -> list[Source]:
        self.set_url_base(self.config.scan_url_bras)
        soup = self.get_html(url=self.config.scan_url_bras)
        if not soup:
            log.error("Failed to obtain sources from SCAN Bras.")
            return []
        sources_uplink = self._get_info_interfaces(soup, uplink=True)
        sources_downlink = self._get_info_interfaces(soup, uplink=False)
        return sources_uplink + sources_downlink
