from scrapper_scanbackup.utils import ScrapperSetting, LayerModel
from scrapper_scanbackup.borde import BordeCisco, BordeHuawei


class UpdaterSources:
    setting: ScrapperSetting

    def __init__(self) -> None:
        self.setting = ScrapperSetting()

    def get_borde(self) -> list[LayerModel]:
        return self.setting.get_data_layer("borde")

    def main_borde(self) -> None:
        borde_info = self.get_borde()
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

        print(borde_sources)
