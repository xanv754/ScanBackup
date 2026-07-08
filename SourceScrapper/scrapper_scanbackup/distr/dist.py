from scrapper_scanbackup.distr.huawei import DistHuawei
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class DistSourceUpdater:
    def _get_dist(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("dist")

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        dist_info = self._get_dist(setting)
        dist_sources = []
        for info in dist_info:
            if info.type.lower() == "huawei":
                huawei = DistHuawei()
                dist = huawei.scrapper(info)
                dist_sources.extend(dist)

        return dist_sources
