from scrapper_scanbackup.ixp.default import IxpDefault
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils import LayerModel, ScrapperSetting


class IxpSourceUpdater:
    def _get_ixp(self, setting: ScrapperSetting) -> list[LayerModel]:
        return setting.get_data_layer("ixp")

    def execute(self, setting: ScrapperSetting) -> list[SourceModel]:
        ixp_info = self._get_ixp(setting)
        ixp_sources = []
        for info in ixp_info:
            if not info.type or info.type.lower() == "":
                ixp = IxpDefault()
                sources = ixp.scrapper(info)
                ixp_sources.extend(sources)

        return ixp_sources
