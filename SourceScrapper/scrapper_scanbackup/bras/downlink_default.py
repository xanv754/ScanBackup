import re
from scrapper_scanbackup.bras.model import BrasPageModel
from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class BrasDefaultDownlink:
    _type_link: str = "DOWNLINK"

    def _extract_capacity(self, name: str) -> int:
        try:
            pattern = r"(\d+)GB"
            match = re.search(pattern, name)
            if match:
                return int(match.group(1))
            raise ValueError(f"{name}: Capacidad no encontrada")
        except Exception as error:
            print(error)
            return 0

    def scrapper(
        self, info: LayerModel, pages: list[BrasPageModel]
    ) -> list[SourceModel]:
        sources = []

        parsed_url = urlparse(info.url)
        url_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

        for page in pages:
            if info.locked:
                html = Scrapper.get_html(page.url, info.credentials)
            else:
                html = Scrapper.get_html(page.url)

            if not html:
                continue

            # Main page
            main = Scrapper.safe_find(
                html, self._type_link, "sección principal (section.content)", "section", class_="content"
            )
            if main is None:
                continue
            first_div = Scrapper.safe_find(
                main, self._type_link, "contenedor de interfaces (div.row)", "div", class_="row"
            )
            if first_div is None:
                continue
            second_div = Scrapper.safe_find(
                first_div, self._type_link, "contenedor de interfaces (div.col-md-12)", "div", class_="col-md-12"
            )
            if second_div is None:
                continue

            # Interfaces list
            container_interfaces = second_div.find_all("div", class_="col-sm-12")
            for container in container_interfaces:
                # Interface name
                subtitulo = Scrapper.safe_find(
                    container, self._type_link, "título de interfaz (li#subtitulo)", "li", id="subtitulo"
                )
                if subtitulo is None:
                    continue
                title = subtitulo.get_text()
                title = title.upper()

                # Skip summaries
                if "- TRAFICO DE RED" not in title:
                    continue

                title = title.replace("- TRÁFICO DE RED", "")
                title = title.replace("- TRAFICO DE RED", "")
                title = title.replace("- TRAFICO DE RD", "")
                title = title.strip()

                # Link .log
                graficas = Scrapper.safe_find(
                    container, self._type_link, "enlace de gráficas (li#graficas)", "li", id="graficas"
                )
                if graficas is None:
                    continue
                anchor = Scrapper.safe_find(
                    graficas, self._type_link, "etiqueta <a> del enlace de gráficas", "a"
                )
                if anchor is None:
                    continue
                href = anchor.get("href")
                if href is None:
                    print(
                        f"{self._type_link}: la etiqueta <a> de gráficas no tiene atributo 'href'. "
                        "Se omite esta interfaz."
                    )
                    continue
                link = url_base + href.replace(".html", ".log")

                # Capacity
                capacity = self._extract_capacity(title)

                sources.append(
                    SourceModel(
                        link=link,
                        enlace=title,
                        capacidad=capacity,
                        model=self._type_link,
                    )
                )
        return sources
