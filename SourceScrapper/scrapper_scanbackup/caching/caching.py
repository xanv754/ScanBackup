import re
from scrapper_scanbackup.caching.model import CachingPageModel
from scrapper_scanbackup.caching.huawei import CachingHuawei
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting, Scrapper
from urllib.parse import urlparse


class CachingSourceUpdater:
    def _get_caching(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("caching")

    def _get_huawei_pages(self, info: LayerModel) -> list[CachingPageModel]:
        if info.locked:
            html = Scrapper.get_html(info.url, info.credentials)
        else:
            html = Scrapper.get_html(info.url)

        if not html:
            return []

        parsed_url = urlparse(info.url)
        url_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Side bar menu
        bar = Scrapper.safe_find(html, "CACHING", "menú lateral (div.sidebar)", "div", class_="sidebar")
        if bar is None:
            return []
        first_menu = Scrapper.safe_find(bar, "CACHING", "lista de menú (ul[role=menu])", "ul", role="menu")
        if first_menu is None:
            return []
        second_menu = Scrapper.safe_find(
            first_menu, "CACHING", "submenú (ul.nav.nav-treeview)", "ul", class_="nav nav-treeview"
        )
        if second_menu is None:
            return []

        # Get pages of services
        services_pages = []
        for option in second_menu.find_all("li"):
            label_tag = Scrapper.safe_find(option, "CACHING", "etiqueta <p> de la opción", "p")
            if label_tag is None:
                continue
            label = label_tag.get_text()
            label = label.strip().upper()

            if "SUMA " in label:
                # Service name
                label = label.replace("SUMA ", "")
                label = label.split(" ")[0]
                label = re.sub(r"\d+$", "", label)

                # Page link
                anchor = Scrapper.safe_find(option, "CACHING", "etiqueta <a> de la página", "a")
                if anchor is None:
                    continue
                page = anchor.get("href")
                if page is None:
                    print(
                        "CACHING: la etiqueta <a> de la página no tiene atributo 'href'. "
                        "Se omite esta página."
                    )
                    continue
                page = url_base + page
                services_pages.append(CachingPageModel(name=label, url=page))

        return services_pages

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        caching_info = self._get_caching(setting)
        caching_sources = []
        for info in caching_info:
            if info.type.lower() == "huawei":
                huawei_pages = self._get_huawei_pages(info)
                if not huawei_pages:
                    continue

                huawei = CachingHuawei()
                huawei_sources = huawei.scrapper(info, huawei_pages)
                caching_sources.extend(huawei_sources)

        return caching_sources
