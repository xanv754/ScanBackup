from scrapper_scanbackup.utils import ScrapperSetting, CSVExporter
from scrapper_scanbackup.borde import BordeSourceUpdater
from scrapper_scanbackup.dint import DintSourceUpdater
from scrapper_scanbackup.distr import DistSourceUpdater
from scrapper_scanbackup.bras import BrasSourceUpdater


class UpdaterSources:
    setting: ScrapperSetting

    def __init__(self) -> None:
        self.setting = ScrapperSetting()

    def _borde_exec(self) -> None:
        borde = BordeSourceUpdater()
        borde_sources = borde.execute(self.setting)
        borde_export = CSVExporter("BORDE", self.setting)
        borde_export.export(borde_sources)

    def _dint_exec(self) -> None:
        dint = DintSourceUpdater()
        dint_sources = dint.execute(self.setting)
        dint_export = CSVExporter("DINT", self.setting)
        dint_export.export(dint_sources)

    def _dist_exec(self) -> None:
        dist = DistSourceUpdater()
        dist_sources = dist.execute(self.setting)
        dist_export = CSVExporter("DIST", self.setting)
        dist_export.export(dist_sources)

    def _bras_exec(self) -> None:
        bras = BrasSourceUpdater()
        bras_sources = bras.execute(self.setting)
        bras_export = CSVExporter("BRAS", self.setting)
        bras_export.export(bras_sources)

    def execute(self, layer: str = "all") -> None:
        # BORDE
        if layer == "all" or layer == "borde":
            self._borde_exec()
            if not layer == "all":
                return

        # DINT
        if layer == "all" or layer == "dint":
            self._dint_exec()
            if not layer == "all":
                return

        # DIST
        if layer == "all" or layer == "dist":
            self._dist_exec()
            if not layer == "all":
                return

        # BRAS
        if layer == "all" or layer == "bras":
            self._bras_exec()
            if not layer == "all":
                return

        if not layer == "all":
            print(f"Capa {layer} no encontrada.")
