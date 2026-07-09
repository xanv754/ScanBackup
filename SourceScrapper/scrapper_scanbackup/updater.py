from pathlib import Path
from scrapper_scanbackup.utils import ScrapperSetting, CSVExporter
from scrapper_scanbackup.borde import BordeSourceUpdater
from scrapper_scanbackup.dint import DintSourceUpdater
from scrapper_scanbackup.distr import DistSourceUpdater
from scrapper_scanbackup.bras import BrasSourceUpdater, IpBrasSourceUpdater
from scrapper_scanbackup.rai import RaiSourceUpdater
from scrapper_scanbackup.ixp import IxpSourceUpdater
from scrapper_scanbackup.caching import CachingSourceUpdater


class UpdaterSources:
    setting: ScrapperSetting

    def __init__(self) -> None:
        self.setting = ScrapperSetting()

    def _borde_exec(self, outpath: Path | None = None) -> None:
        borde = BordeSourceUpdater()
        borde_sources = borde.execute(self.setting)
        borde_export = CSVExporter("BORDE", self.setting, outdir=outpath)
        borde_export.export(borde_sources)

    def _dint_exec(self, outpath: Path | None = None) -> None:
        dint = DintSourceUpdater()
        dint_sources = dint.execute(self.setting)
        dint_export = CSVExporter("DINT", self.setting, outdir=outpath)
        dint_export.export(dint_sources)

    def _dist_exec(self, outpath: Path | None = None) -> None:
        dist = DistSourceUpdater()
        dist_sources = dist.execute(self.setting)
        dist_export = CSVExporter("DIST", self.setting, outdir=outpath)
        dist_export.export(dist_sources)

    def _bras_exec(self, outpath: Path | None = None) -> None:
        bras = BrasSourceUpdater()
        bras_sources = bras.execute(self.setting)
        bras_export = CSVExporter("BRAS", self.setting, outdir=outpath)
        bras_export.export(bras_sources)

    def _rai_exec(self, outpath: Path | None = None) -> None:
        rai = RaiSourceUpdater()
        rai_sources = rai.execute(self.setting)
        rai_export = CSVExporter("RAI", self.setting, outdir=outpath)
        rai_export.export(rai_sources)

    def _ixp_exec(self, outpath: Path | None = None) -> None:
        ixp = IxpSourceUpdater()
        ixp_sources = ixp.execute(self.setting)
        ixp_export = CSVExporter("IXP", self.setting, outdir=outpath)
        ixp_export.export(ixp_sources)

    def _ip_exec(self, outpath: Path | None = None) -> None:
        ip = IpBrasSourceUpdater()
        ip_sources = ip.execute(self.setting)
        ip_export = CSVExporter("IP_BRAS", self.setting, outdir=outpath, ip=True)
        ip_export.export(ip_sources)

    def _caching_exec(self, outpath: Path | None = None) -> None:
        caching = CachingSourceUpdater()
        caching_sources = caching.execute(self.setting)
        caching_export = CSVExporter("CACHING", self.setting, outdir=outpath)
        caching_export.export(caching_sources)

    def execute(self, layer: str = "all", outpath: Path | None = None) -> None:
        layer = layer.lower().strip()

        # BORDE
        if layer == "all" or layer == "borde":
            self._borde_exec(outpath=outpath)
            if not layer == "all":
                return

        # DINT
        if layer == "all" or layer == "dint":
            self._dint_exec(outpath=outpath)
            if not layer == "all":
                return

        # DIST
        if layer == "all" or layer == "dist":
            self._dist_exec(outpath=outpath)
            if not layer == "all":
                return

        # BRAS
        if layer == "all" or layer == "bras":
            self._bras_exec(outpath=outpath)
            if not layer == "all":
                return

        # IP BRAS
        if (
            layer == "all"
            or layer == "ip"
            or layer == "ip_bras"
            or layer == "ipbras"
            or layer == "ip-bras"
        ):
            self._ip_exec(outpath=outpath)
            if not layer == "all":
                return

        # RAI
        if layer == "all" or layer == "rai":
            self._rai_exec(outpath=outpath)
            if not layer == "all":
                return

        # IXP
        if layer == "all" or layer == "ixp":
            self._ixp_exec(outpath=outpath)
            if not layer == "all":
                return

        # CACHING
        if layer == "all" or layer == "caching":
            self._caching_exec(outpath=outpath)
            if not layer == "all":
                return

        if not layer == "all":
            print(f"Capa {layer} no encontrada.")
