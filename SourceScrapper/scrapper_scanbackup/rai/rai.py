from scrapper_scanbackup.rai.huawei import RaiHuawei
from scrapper_scanbackup.rai.zte import RaiZte
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class RaiSourceUpdater:
    def _get_rai(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("rai")

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        rai_info = self._get_rai(setting)
        rai_sources = []
        for info in rai_info:
            if info.type.lower() == "huawei":
                huawei = RaiHuawei()
                huawei = huawei.scrapper(info)
                rai_sources.extend(huawei)
            if info.type.lower() == "zte":
                zte = RaiZte()
                zte = zte.scrapper(info)
                rai_sources.extend(zte)

        return rai_sources
