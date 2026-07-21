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
        main = Scrapper.safe_find(
            html, "IP_BRAS", "sección principal (section.content)", "section", class_="content"
        )
        if main is None:
            return sources
        first_div = Scrapper.safe_find(
            main, "IP_BRAS", "contenedor de interfaces (div.row)", "div", class_="row"
        )
        if first_div is None:
            return sources
        second_div = Scrapper.safe_find(
            first_div, "IP_BRAS", "contenedor de interfaces (div.col-md-12)", "div", class_="col-md-12"
        )
        if second_div is None:
            return sources

        # Interfaces list
        container_interfaces = second_div.find_all("div", class_="col-sm-12")
        for container in container_interfaces:
            # Interface name
            subtitulo = Scrapper.safe_find(
                container, "IP_BRAS", "título de interfaz (li#subtitulo)", "li", id="subtitulo"
            )
            if subtitulo is None:
                continue
            title = subtitulo.get_text()
            title = title.upper()

            # Skip Summaries
            junk_word = "SUMATORIA TOTAL BRAS"
            if junk_word in title:
                continue

            title = title.replace("SUMATORIA", "")
            title = title.split(" - ")[0]
            title = title.strip()

            # Link .log
            graficas = Scrapper.safe_find(
                container, "IP_BRAS", "enlace de gráficas (li#graficas)", "li", id="graficas"
            )
            if graficas is None:
                continue
            anchor = Scrapper.safe_find(
                graficas, "IP_BRAS", "etiqueta <a> del enlace de gráficas", "a"
            )
            if anchor is None:
                continue
            href = anchor.get("href")
            if href is None:
                print(
                    "IP_BRAS: la etiqueta <a> de gráficas no tiene atributo 'href'. "
                    "Se omite esta interfaz."
                )
                continue
            link = url_base + href.replace(".html", ".log")

            sources.append(IpSourceModel(link=link, enlace=title))

        return sources
