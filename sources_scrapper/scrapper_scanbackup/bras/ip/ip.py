from scrapper_scanbackup.bras.ip.default import IpBrasDefault
from scrapper_scanbackup.model import IpSourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class IpBrasSourceUpdater:
    def _get_ip(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("ip_bras")

    def execute(self, setting: ScrapperSetting) -> list[IpSourceModel]:
        ip_info = self._get_ip(setting)
        ip_sources = []
        for info in ip_info:
            if not info.type or info.type.lower() == "":
                ip = IpBrasDefault()
                sources = ip.scrapper(info)
                ip_sources.extend(sources)

        return ip_sources
