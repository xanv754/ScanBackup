from scanbackup.constants import LayerName
from scanbackup.updater.data.bbip import BBIPUpdaterHandler
from scanbackup.updater.data.dailySummary import DailySummaryUpdaterHandler
from scanbackup.updater.data.ipBras import IPBrasUpdaterHandler
from scanbackup.updater.sources.borde import BordeHuawei, BordeCisco, BordeJuniper
from scanbackup.updater.sources.bras import BrasHuawei
from scanbackup.updater.sources.caching import CachingHuawei
from scanbackup.updater.sources.rai import RaiHuawei, RaiZte
from scanbackup.updater.sources.ixp import IxpHuawei
from scanbackup.updater.sources.ipBras import IPBrasHuawei
from scanbackup.utils import (
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
    """Handler class for layer data updates."""

    def __init__(
        self, layer: str, uri: str, date: str | None = None, force: bool = False
    ) -> None:
        if layer == LayerName.DAILY_SUMMARY:
            self._updater_daily_summary(uri=uri, date=date, force=force)
        elif layer == LayerName.IP_BRAS:
            self._updater_ip_bras(uri=uri, date=date, force=force)
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
                log.info(f"System Updater. {layer}: Data de la capa cargada exitosamente")
            else:
                log.error(f"System Updater. {layer}: Fallo en la carga de la data de la capa")
        except Exception as error:
            log.error(f"System Updater. {layer}: Fallo al actualizar los datos de la capa del BBIP en el sistema - {error}")
        finally:
            log.info(f"System Updater. {layer}: Actualización finalizada")

    def _updater_ip_bras(self, uri: str, date: str | None, force: bool) -> None:
        """Updater IP history collection in database."""
        try:
            ip_history_handler = IPBrasUpdaterHandler()
            data = ip_history_handler.get_data(date=date, force=force)
            status_operation = ip_history_handler.load_data(data=data, uri=uri)
            if status_operation:
                log.info("BBIP Updater. IPBRAS: Data de la capa cargada exitosamente")
            else:
                log.error(f"System Updater. IPBRAS: Fallo en la carga de la data de la capa")
        except Exception as error:
            log.error(f"System Updater. IPBRAS: Fallo al actualizar los datos de la capa del BBIP en el sistema - {error}")
        finally:
            log.info(f"System Updater. IPBRAS: Actualización finalizada")

    def _updater_daily_summary(self, uri: str, date: str | None, force: bool) -> None:
        """Updater daily summary collection in database."""
        try:
            log.info("Inicio de actualización de los resúmenes diarios del sistema...")
            daily_handler = DailySummaryUpdaterHandler()
            reports = daily_handler.get_data(date=date, force=force)
            status_operation = daily_handler.load_data(data=reports, uri=uri)
            if status_operation:
                log.info(f"System Updater. DAILY SUMMARY: Data de la capa cargada exitosamente")
            else:
                log.error(f"System Updater. DAILY SUMMARY: Fallo en la carga de la data de la capa")
        except Exception as error:
            log.error(f"System Updater. DAILY SUMMARY: Fallo al actualizar los datos de la capa del BBIP en el sistema - {error}")
        finally:
            log.info("System Updater. DAILY SUMMARY: Actualización de los resúmenes diarios finalizada")


class UpdaterSourceHandler:
    """Handler class for source updates."""

    def __init__(self, layer: str, dev: bool = False) -> None:
        try:
            log.info(f"Inicio de actualización de la capa {layer}...")
            if layer == LayerName.BORDE:
                if dev: url = URLBordeCiscoEnvironment(dev=True).get_url()
                else: url = URLBordeCiscoEnvironment().get_url()
                scrapper_cisco = BordeCisco(url=url, layer=LayerName.BORDE, add_sources=True)
                status_update = scrapper_cisco.run()
                if dev: url = URLBordeHuaweiEnvironment(dev=True).get_url()
                else: url = URLBordeHuaweiEnvironment().get_url()
                scrapper_huawei = BordeHuawei(url=url, layer=LayerName.BORDE)
                status_update = scrapper_huawei.run()
                if dev: url = URLBordeJuniperEnvironment(dev=True).get_url()
                else: url = URLBordeJuniperEnvironment().get_url()
                scrapper_juniper = BordeJuniper(url=url, layer=LayerName.BORDE, add_sources=True)
                status_update = scrapper_juniper.run()
            elif layer == LayerName.BRAS:
                if dev: url = URLBrasHuaweiEnvironment(dev=True).get_url()
                else: url = URLBrasHuaweiEnvironment().get_url()
                scrapper_huawei = BrasHuawei(url=url, layer=LayerName.BRAS)
                status_update = scrapper_huawei.run()
            elif layer == LayerName.CACHING:
                if dev: url = URLCachingHuaweiEnvironment(dev=True).get_url()
                else: url = URLCachingHuaweiEnvironment().get_url()
                scrapper_huawei = CachingHuawei(url=url, layer=LayerName.CACHING)
                status_update = scrapper_huawei.run()
            elif layer == LayerName.RAI:
                if dev: url = URLRaiHuaweiEnvironment(dev=True).get_url()
                else: url = URLRaiHuaweiEnvironment().get_url()
                scrapper_huawei = RaiHuawei(url=url, layer=LayerName.RAI)
                status_update = scrapper_huawei.run()
                if dev: url = URLRaiZteEnvironment(dev=True).get_url()
                else: url = URLRaiZteEnvironment().get_url()
                scrapper_zte = RaiZte(url=url, layer=LayerName.RAI, add_sources=True)
                status_update = scrapper_zte.run()
            elif layer == LayerName.IXP:
                if dev: url = URLIxpEnvironment(dev=True).get_url()
                else: url = URLIxpEnvironment().get_url()
                scrapper_ixp = IxpHuawei(url=url, layer=LayerName.IXP)
                status_update = scrapper_ixp.run()
            elif layer == LayerName.IP_BRAS:
                if dev: url = URLIpBrasEnvironment(dev=True).get_url()
                else: url = URLIpBrasEnvironment().get_url()
                scrapper_ip_bras = IPBrasHuawei(url=url, layer=LayerName.IP_BRAS)
                status_update = scrapper_ip_bras.run()
            else:
                raise Exception("Capa no válida para actualizar los enlaces")

            if status_update:
                log.info(f"Enlaces de la capa {layer} actualizados")
            else:
                log.error(f"Fallo al actualizar los enlaces para la capa {layer}")
        except Exception as error:
            log.error(f"Fallo al intentar actualizar los enlaces de la capa {layer} - {error}")
            return None