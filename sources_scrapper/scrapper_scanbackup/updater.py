from scrapper_scanbackup.utils import ScrapperSetting, LayerModel, CSVExporter
from scrapper_scanbackup.borde import BordeSourceUpdater


class UpdaterSources:
    setting: ScrapperSetting

    def __init__(self) -> None:
        self.setting = ScrapperSetting()

    def execute(self) -> list[LayerModel]:
        # BORDE
        borde = BordeSourceUpdater()
        borde_sources = borde.execute(self.setting)
        borde_export = CSVExporter("BORDE", self.setting)
        borde_export.export(borde_sources)
