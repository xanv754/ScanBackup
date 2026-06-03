from scrapper_scanbackup.dint.huawei import DintHuawei
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class DintSourceUpdater:
    def _get_dint(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("dint")

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        dint_info = self._get_dint(setting)
        dint_sources = []
        for info in dint_info:
            if info.type.lower() == "huawei":
                huawei = DintHuawei()
                dint = huawei.scrapper(info)
                dint_sources.extend(dint)

        return dint_sources
