from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import IpSourceModel
from urllib.parse import urlparse


class IpBrasDefault:
    def scrapper(self, info: LayerModel) -> list[IpSourceModel]:
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
        main = html.find("section", class_="content")
        first_div = main.find("div", class_="row")
        second_div = first_div.find("div", class_="col-md-12")

        # Interfaces list
        container_interfaces = second_div.find_all("div", class_="col-sm-12")
        for container in container_interfaces:
            # Interface name
            title = container.find("li", id="subtitulo").get_text()
            title = title.upper()

            # Skip Summaries
            junk_word = "SUMATORIA TOTAL BRAS"
            if junk_word in title:
                continue

            title = title.replace("SUMATORIA", "")
            title = title.split(" - ")[0]
            title = title.strip()

            # Link .log
            link = url_base + container.find("li", id="graficas").find("a").get(
                "href"
            ).replace(".html", ".log")

            sources.append(IpSourceModel(link=link, name=title))

        return sources
