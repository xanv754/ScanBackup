import re
from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class DistHuawei:
    _layer: str = "HUAWEI"

    def _extract_capacity(self, name: str) -> int:
        try:
            pattern = r"(\d+)GE?"
            match = re.search(pattern, name)
            if match:
                return int(match.group(1))
            raise ValueError(f"{name}: Capacidad no encontrada")
        except Exception as error:
            print(error)
            return 0

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
        main = Scrapper.safe_find(html, self._layer, "main (id=main)", id="main")
        if main is None:
            return sources

        # Interfaces list
        container_interfaces = Scrapper.safe_find(
            main, self._layer, "contenedor de interfaces (div.row)", "div", class_="row"
        )
        if container_interfaces is None:
            return sources

        # Info Interface
        for div in container_interfaces.find_all("div", recursive=False):
            # Interface Name
            subtitulo = Scrapper.safe_find(
                div, self._layer, "título de interfaz (li#subtitulo)", "li", id="subtitulo"
            )
            if subtitulo is None:
                continue
            title = subtitulo.get_text()
            title = title.upper()
            title = title.replace("ROUTER", "")
            title = title.replace("- TRÁFICO DE RED", "")
            title = title.replace("- TRAFICO DE RED", "")
            title = title.replace("- TRAFICO DE RD", "")
            title = title.strip()

            # Link .log
            graficas = Scrapper.safe_find(
                div, self._layer, "enlace de gráficas (li#graficas)", "li", id="graficas"
            )
            if graficas is None:
                continue
            anchor = Scrapper.safe_find(
                graficas, self._layer, "etiqueta <a> del enlace de gráficas", "a"
            )
            if anchor is None:
                continue
            href = anchor.get("href")
            if href is None:
                print(
                    f"{self._layer}: la etiqueta <a> de gráficas no tiene atributo 'href'. "
                    "Se omite esta interfaz."
                )
                continue
            link = url_base + href.replace(".html", ".log")

            # Capacity
            capacity = self._extract_capacity(title)

            sources.append(
                SourceModel(
                    link=link, enlace=title, capacidad=capacity, model=self._layer
                )
            )

        return sources
