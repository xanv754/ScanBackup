from systemgrd.constants import LayerName
from systemgrd.updater.data.bbip import BBIPUpdaterHandler
from systemgrd.updater.data.dailyReport import DailyReportUpdaterHandler
from systemgrd.updater.data.ipHistory import IPHistoryUpdaterHandler
from systemgrd.updater.sources.borde import BordeHuawei, BordeCisco, BordeJuniper
from systemgrd.updater.sources.bras import BrasHuawei
from systemgrd.updater.sources.caching import CachingHuawei
from systemgrd.updater.sources.rai import RaiHuawei, RaiZte
from systemgrd.utils import (
    URLBordeCiscoEnvironment,
    URLBordeJuniperEnvironment,
    URLBordeHuaweiEnvironment,
    URLBrasHuaweiEnvironment,
    URLCachingHuaweiEnvironment,
    URLIpBrasEnvironment,
    URLIxpEnvironment,
    URLRaiHuaweiEnvironment,
    URLRaiZteEnvironment,
    log
)


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
                log.info(f"Data de la capa: {layer} cargado exitosamente")
            else:
                log.error(f"Carga de la data de la capa: {layer} fallida")
        except Exception as error:
            log.error(f"Fallo al actualizar los datos de la capa: {layer} del BBIP en el sistema - {error}")

    def _updater_ip_history(self, uri: str, date: str | None, force: bool) -> None:
        """Updater IP history collection in database."""
        try:
            ip_history_handler = IPHistoryUpdaterHandler()
            data = ip_history_handler.get_data(date=date, force=force)
            status_operation = ip_history_handler.load_data(data=data, uri=uri)
            if status_operation:
                log.info("Data de la capa: IP_BRAS cargado exitosamente")
            else:
                log.error("Carga de la data de la capa: IP_BRAS fallida")
        except Exception as error:
            log.error(f"Fallo al actualizar los datos de la capa: IP_BRAS del BBIP en el sistema - {error}")

    def _updater_daily_summary(self, uri: str, date: str | None, force: bool) -> None:
        """Updater daily summary collection in database."""
        try:
            log.info("Inicio de actualización de reportes diarios del sistema...")
            daily_handler = DailyReportUpdaterHandler()
            reports = daily_handler.get_data(date=date, force=force)
            status_operation = daily_handler.load_data(data=reports, uri=uri)
            if status_operation:
                log.info("Actualización de reportes diarios cargado exitosamente")
            else:
                log.error(f"Carga de los reportes diarios fallido")
        except Exception as error:
            log.error(f"Fallo al actualizar los datos de los reportes diarios en el sistema - {error}")
        finally:
            log.info("Actualización de reportes diarios finalizada")


class UpdaterSourceHandler:

    def __init__(self, layer: str, dev: bool = False) -> None:
        try:
            log.info(f"Inicio de actualización de la capa {layer}...")
            if layer == LayerName.BORDE:
                if dev: url = URLBordeHuaweiEnvironment(dev=True).get_url()
                else: url = URLBordeHuaweiEnvironment(prod=True).get_url()
                scrapper_huawei = BordeHuawei(url=url, layer=LayerName.BORDE)
                status_update = scrapper_huawei.run()
                if dev: url = URLBordeCiscoEnvironment(dev=True).get_url()
                else: url = URLBordeCiscoEnvironment(prod=True).get_url()
                scrapper_cisco = BordeCisco(url=url, layer=LayerName.BORDE, add_sources=True)
                status_update = scrapper_cisco.run()
                if dev: url = URLBordeJuniperEnvironment(dev=True).get_url()
                else: url = URLBordeJuniperEnvironment(prod=True).get_url()
                scrapper_juniper = BordeJuniper(url=url, layer=LayerName.BORDE, add_sources=True)
                status_update = scrapper_juniper.run()
            elif layer == LayerName.BRAS:
                if dev: url = URLBrasHuaweiEnvironment(dev=True).get_url()
                else: url = URLBrasHuaweiEnvironment(prod=True).get_url()
                scrapper_huawei = BrasHuawei(url=url, layer=LayerName.BRAS)
                status_update = scrapper_huawei.run()
            elif layer == LayerName.CACHING:
                if dev: url = URLCachingHuaweiEnvironment(dev=True).get_url()
                else: url = URLCachingHuaweiEnvironment(prod=True).get_url()
                scrapper_huawei = CachingHuawei(url=url, layer=LayerName.CACHING)
                status_update = scrapper_huawei.run()
            elif layer == LayerName.RAI:
                if dev: url = URLRaiHuaweiEnvironment(dev=True).get_url()
                else: url = URLRaiHuaweiEnvironment(prod=True).get_url()
                scrapper_huawei = RaiHuawei(url=url, layer=LayerName.RAI)
                status_update = scrapper_huawei.run()
                if dev: url = URLRaiZteEnvironment(dev=True).get_url()
                else: url = URLRaiZteEnvironment(prod=True).get_url()
                scrapper_zte = RaiZte(url=url, layer=LayerName.RAI, add_sources=True)
                status_update = scrapper_zte.run()
            else:
                raise Exception("Capa no válida para actualizar los enlaces")

            if status_update:
                log.info(f"Enlaces de la capa {layer} actualizados")
            else:
                log.error(f"Fallo al actualizar los enlaces para la capa {layer}")
        except Exception as error:
            log.error(f"Fallo al intentar actualizar los enlaces de la capa {layer} - {error}")
            return None


if __name__ == "__main__":
    UpdaterSourceHandler(layer="BORDE")