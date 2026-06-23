import re
from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class RaiHuawei:
    _layer: str = "HUAWEI"

    def _extract_capacity(self, name: str) -> int:
        try:
            # Format: Before of "GE": CGEX/Y/Z
            if "GE" in name:
                pattern = r"(\d+)GE"
                match = re.search(pattern, name)
                number = match.group(1) if match else None
                if number:
                    return int(number)
            raise ValueError(f"{name}: Capacidad no encontrada")
        except Exception as error:
            print(error)
            return 0

    def scrapper(self, info: LayerModel) -> list[SourceModel]:
        sources = []

        if info.locked:
            html = Scrapper.get_html(info.url, info.credentials)
        else:
            html = Scrapper.get_html(info.url)

        if not html:
            return sources

        parsed_url = urlparse(info.url)
        url_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Main page
        main = html.find(id="main")

        # Interfaces list
        container_interfaces = main.find("div", class_="row")

        # Info Interface
        for div in container_interfaces.find_all("div", recursive=False):
            # Interface Name
            title = div.find("li", id="subtitulo").get_text()
            title = title.upper()

            title = title.replace("ROUTER", "")
            title = title.replace("- TRÁFICO DE RED", "")
            title = title.replace("- TRAFICO DE RED", "")
            title = title.strip()

            # Link .log
            link = url_base + div.find("li", id="graficas").find("a").get(
                "href"
            ).replace(".html", ".log")

            # Capacity
            capacity = self._extract_capacity(title)

            sources.append(
                SourceModel(
                    link=link, enlace=title, capacidad=capacity, model=self._layer
                )
            )

        return sources
