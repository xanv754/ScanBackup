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
        bar = html.find("div", class_="sidebar")
        first_menu = bar.find("ul", role="menu")
        second_menu = first_menu.find("ul", class_="nav nav-treeview")

        # Get pages of services
        services_pages = []
        for option in second_menu.find_all("li"):
            label = option.find("p").get_text()
            label = label.strip().upper()

            if "SUMA " in label:
                # Service name
                label = label.replace("SUMA ", "")
                label = label.split(" ")[0]
                label = re.sub(r"\d+$", "", label)

                # Page link
                page = option.find("a").get("href")
                page = url_base + page
                services_pages.append(CachingPageModel(name=label, url=page))

        return services_pages

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        caching_info = self._get_caching(setting)
        caching_sources = []
        for info in caching_info:
            if info.type == "huawei":
                huawei_pages = self._get_huawei_pages(info)
                if not huawei_pages:
                    return []

                huawei = CachingHuawei()
                huawei_sources = huawei.scrapper(info, huawei_pages)
                caching_sources.extend(huawei_sources)

        return caching_sources
