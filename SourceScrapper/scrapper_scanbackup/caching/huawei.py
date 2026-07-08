import re
from scrapper_scanbackup.caching.model import CachingPageModel
from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class CachingHuawei:
    def _extract_capacity(self, name: str) -> int:
        try:
            pattern = r"(\d+)GE?B?"
            match = re.search(pattern, name)
            if match:
                return int(match.group(1))
            raise ValueError(f"{name}: Capacidad no encontrada")
        except Exception as error:
            print(error)
            return 0

    def scrapper(
        self, info: LayerModel, services: list[CachingPageModel]
    ) -> list[SourceModel]:
        sources = []

        parsed_url = urlparse(info.url)
        url_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

        for service in services:
            if info.locked:
                html = Scrapper.get_html(service.url, info.credentials)
            else:
                html = Scrapper.get_html(service.url)

            if not html:
                return []

            # Main page
            main = html.find("section", class_="content")
            first_div = main.find("div", class_="row")
            second_div = first_div.find("div", class_="col-md-12")

            # Interfaces list
            container_interfaces = second_div.find_all("div", class_="col-sm-12")
            for container in container_interfaces:
                # Interface name
                title = container.find("li", id="subtitulo").get_text()
                title = title.upper()

                # Skip summaries
                if "SUMATORIA" in title:
                    continue

                title = title.replace("ROUTER ", "")
                title = title.replace("- TRÁFICO DE RED", "")
                title = title.replace("- TRAFICO DE RED", "")
                title = title.replace("- TRAFICO DE RD", "")
                title = title.strip()

                # Link .log
                link = url_base + container.find("li", id="graficas").find("a").get(
                    "href"
                ).replace(".html", ".log")

                # Capacity
                capacity = self._extract_capacity(title)

                sources.append(
                    SourceModel(
                        link=link, enlace=title, capacidad=capacity, model=service.name
                    )
                )

        return sources
