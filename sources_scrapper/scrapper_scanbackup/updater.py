from scrapper_scanbackup.utils import ScrapperSetting, CSVExporter
from scrapper_scanbackup.borde import BordeSourceUpdater
from scrapper_scanbackup.dint import DintSourceUpdater
from scrapper_scanbackup.distr import DistSourceUpdater


class UpdaterSources:
    setting: ScrapperSetting

    def __init__(self) -> None:
        self.setting = ScrapperSetting()

    def execute(self) -> None:
        # BORDE
        borde = BordeSourceUpdater()
        borde_sources = borde.execute(self.setting)
        borde_export = CSVExporter("BORDE", self.setting)
        borde_export.export(borde_sources)

        # DINT
        dint = DintSourceUpdater()
        dint_sources = dint.execute(self.setting)
        dint_export = CSVExporter("DINT", self.setting)
        dint_export.export(dint_sources)

        # DIST
        dist = DistSourceUpdater()
        dist_sources = dist.execute(self.setting)
        dist_export = CSVExporter("DIST", self.setting)
        dist_export.export(dist_sources)
