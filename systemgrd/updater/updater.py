from systemgrd.constants import LayerName
from systemgrd.updater.data.bbip import BBIPUpdaterHandler
from systemgrd.updater.data.dailyReport import DailyReportUpdaterHandler
from systemgrd.updater.data.ipHistory import IPHistoryUpdaterHandler
from systemgrd.updater.sources.borde import BordeSourceScrapping
from systemgrd.updater.sources.bras import BrasSourceScrapping
from systemgrd.updater.sources.caching import CachingSourceScrapping
from systemgrd.updater.sources.rai import RAISourceScrapping
from systemgrd.updater.sources.ipbras import IPBrasSourceScrapping
from systemgrd.utils import log


class UpdaterHandler:

    def __init__(
        self, layer: str, uri: str, date: str | None = None, force: bool = False
    ) -> None:
        if layer == LayerName.DAILY_REPORT:
            self._updater_daily_summary(uri=uri, date=date, force=force)
        elif layer == LayerName.IP_BRAS:
            self._updater_ip_history(uri=uri, date=date, force=force)
        else:
            self._updater_bbip(layer=layer, uri=uri, date=date, force=force)

    def _updater_bbip(
        self, layer: str, uri: str, date: str | None, force: bool
    ) -> None:
        """Updater BBIP collection in database."""
        try:
            bbip_handler = BBIPUpdaterHandler()
            data = bbip_handler.get_data(layer=layer, date=date, force=force)
            status_operation = bbip_handler.load_data(layer=layer, data=data, uri=uri)
            if status_operation:
                log.info(f"Data de {layer} cargado exitosamente")
            else:
                log.error(f"Carga de la data de {layer} fallida")
        except Exception as e:
            log.error(f"Failed to load data of {layer} layer. {e}")

    def _updater_ip_history(self, uri: str, date: str | None, force: bool) -> None:
        """Updater IP history collection in database."""
        try:
            ip_history_handler = IPHistoryUpdaterHandler()
            data = ip_history_handler.get_data(date=date, force=force)
            status_operation = ip_history_handler.load_data(data=data, uri=uri)
            if status_operation:
                log.info("Data de IPBras cargado exitosamente")
            else:
                log.error("Carga de la data de IPBras fallida")
        except Exception as e:
            log.error(f"Failed to load data of IPBras layer. {e}")

    def _updater_daily_summary(self, uri: str, date: str | None, force: bool) -> None:
        """Updater daily summary collection in database."""
        try:
            daily_handler = DailyReportUpdaterHandler()
            reports = daily_handler.get_data(date=date, force=force)
            status_operation = daily_handler.load_data(data=reports, uri=uri)
            if status_operation:
                log.info("Actualización de reportes diarios cargado exitosamente")
            else:
                log.error(f"Carga de los reportes diarios fallido")
        except Exception as e:
            log.error(f"Failed to load data of daily summary. {e}")


class UpdaterSourceHandler:

    def __init__(self, layer: str) -> None:
        try:
            log.info(f"Inicio de actualización de la capa {layer}...")
            if layer == LayerName.BORDE:
                scrapper = BordeSourceScrapping()
            elif layer == LayerName.BRAS:
                scrapper = BrasSourceScrapping()
            elif layer == LayerName.CACHING:
                scrapper = CachingSourceScrapping()
            elif layer == LayerName.RAI:
                scrapper = RAISourceScrapping()
            elif layer == LayerName.IP_BRAS:
                scrapper = IPBrasSourceScrapping()
            else:
                raise Exception("Layer not valid to updater sources")

            links = scrapper.get_sources()
            log.info(f"Guardando {layer} capa...")
            status_update = scrapper.save_sources(sources=links, layer=layer)
            if status_update:
                log.info(f"Enlaces de SCAN {layer} actualizados.")
            else:
                log.error(f"Fallo al actualizar los enlaces de SCAN {layer}.")
        except Exception as e:
            log.error(f"Failed to load data of {layer} sources. {e}")
            return None
