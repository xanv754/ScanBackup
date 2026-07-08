import re
from scrapper_scanbackup.bras.uplink_default import BrasDefaultUplink
from scrapper_scanbackup.bras.downlink_default import BrasDefaultDownlink
from scrapper_scanbackup.bras.model import BrasPageModel
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting, Scrapper
from urllib.parse import urlparse


class BrasSourceUpdater:
    def _get_dint(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("bras")

    def _get_default_pages(self, info: LayerModel) -> list[BrasPageModel]:
        if info.locked:
            html = Scrapper.get_html(info.url, info.credentials)
        else:
            html = Scrapper.get_html(info.url)

        if not html:
            return []

        parsed_url = urlparse(info.url)
        url_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Side bar menu
        bar = html.find("div", class_="sidebar")
        list_menu = bar.find("ul", role="menu")

        # Get BRAS list of menu
        bras_menu = []
        for menu in list_menu.find_all("li"):
            if (
                menu.has_attr("class")
                and "nav-item" in menu["class"]
                and "menu" in menu["class"]
            ):
                label = menu.find("a").get_text()
                label = label.strip()
                if re.fullmatch(r"[A-Z]{3}-BRAS", label):
                    bras_menu.append((label, menu))

        # Get BRAS options inside the options menu
        bras_options = []
        for brasname, menu in bras_menu:
            list_content = menu.find("ul")
            for content in list_content.find_all("li"):
                options = content.find_all("p")
                for option in options:
                    text = option.get_text()
                    if "UPLINK POR BRAS" in text:
                        bras_options.append((brasname, content, "UPLINK"))
                    elif "DOWNLINK POR BRAS" in text:
                        bras_options.append((brasname, content, "DOWNLINK"))

        # Get BRAS page inside the BRAS options
        bras_pages = []
        for brasname, content, type_bras in bras_options:
            list_option = content.find_all("li")
            for option in list_option:
                label = option.find("p").get_text()

                pattern = rf"^{re.escape(brasname)}-\d{{2}}$"
                if re.match(pattern, label):
                    link = option.find("a").get("href").strip()
                    link = url_base + link
                    bras_pages.append(
                        BrasPageModel(
                            name=label,
                            url=link,
                            type_link=type_bras,
                        )
                    )

        return bras_pages

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        bras_info = self._get_dint(setting)
        bras_sources = []
        for info in bras_info:
            if not info.type or info.type.lower() == "":
                pages = self._get_default_pages(info)
                uplink_pages = [page for page in pages if page.type_link == "UPLINK"]
                downlink_pages = [
                    page for page in pages if page.type_link == "DOWNLINK"
                ]

                bras_uplink = BrasDefaultUplink()
                bras_uplink_sources = bras_uplink.scrapper(info, uplink_pages)
                bras_sources.extend(bras_uplink_sources)

                bras_downlink = BrasDefaultDownlink()
                bras_downlink_sources = bras_downlink.scrapper(info, downlink_pages)
                bras_sources.extend(bras_downlink_sources)

        return bras_sources
