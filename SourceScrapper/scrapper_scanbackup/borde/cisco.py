from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class BordeCisco:
    _layer: str = "CISCO"

    def scrapper(self, info: LayerModel) -> list:
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
        # print(main.prettify())

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

            sources.append(SourceModel(link=link, enlace=title, model=self._layer))
        return sources
