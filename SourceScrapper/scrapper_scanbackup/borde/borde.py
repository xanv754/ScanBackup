from scrapper_scanbackup.borde.cisco import BordeCisco
from scrapper_scanbackup.borde.huawei import BordeHuawei
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class BordeSourceUpdater:
    def _get_borde(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("borde")

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        borde_info = self._get_borde(setting)
        borde_sources = []
        for info in borde_info:
            if info.type.lower() == "cisco":
                cisco = BordeCisco()
                borde = cisco.scrapper(info)
                borde_sources.extend(borde)
            if info.type.lower() == "huawei":
                huawei = BordeHuawei()
                borde = huawei.scrapper(info)
                borde_sources.extend(borde)

        return borde_sources
