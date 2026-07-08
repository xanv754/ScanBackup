import re
from scrapper_scanbackup.utils import Scrapper, LayerModel
from scrapper_scanbackup.model import SourceModel
from urllib.parse import urlparse


class IxpDefault:
    def _extract_type(self, name: str) -> str:
        try:
            # Format: "POSICION <TYPE>"
            if re.search(r"POSICION", name):
                if match := re.search(
                    r"POSICION\s+\w+\s+-\s+(\w+(?:\s+\w+)?)\s*\)", name
                ):
                    return match.group(1)
                if match := re.search(r"POSICION\s+(\w+)\s*\)", name):
                    return match.group(1)

            # Format: "PEERING PRIVADO <TYPE>"
            if re.search(r"PEERING PRIVADO", name):
                if match := re.search(r"PEERING PRIVADO\s+([^)]+)\)", name):
                    parts = [p.strip() for p in match.group(1).split("-")]
                    non_cantv = [p for p in parts if p != "CANTV"]
                    if non_cantv:
                        return non_cantv[0]
                raise ValueError(f"{name}: Tipo no encontrado")

            # Search: <TYPE>
            if match := re.search(r"-\s+(\w+(?:\s+\w+)?)\s*\)", name):
                return match.group(1)

            raise ValueError(f"{name}: Tipo no encontrado")
        except Exception as error:
            print(error)
            return "IXP"

    def _extract_capacity(self, name: str) -> int:
        try:
            # Format: Before of "GB": CGB X/Y/Z
            if "GB" in name:
                pattern = r"(\d+)GB"
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

            # Type IXP
            type_ixp = self._extract_type(title)

            sources.append(
                SourceModel(link=link, enlace=title, capacidad=capacity, model=type_ixp)
            )

        return sources
