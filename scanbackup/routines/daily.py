import os
import click
import pandas as pd
from datetime import datetime, timedelta, timezone
from scanbackup.constants import (
    LayerName, DataPath, 
    HeaderBBIP, HeaderDailySummary, 
    HeaderIPBras, header_daily_ip_bras,
    foldername_BBIP_SCAN, header_scan_ip_bras, 
    header_scan_bbip, header_daily_bbip
)
from scanbackup.utils import log


FACTOR_BBIP: float = 0.000000008022


class GenerateDailySummary:
    _export_decimal = "."
    _folder_path = DataPath.SCAN_REPORT_DAILY
    _separator_data = ";"
    _separator_name = ";"
    date: str
    layers: list[str]
    
    def __init__(self, date: str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d"), layer: str | None = None):
        if layer: self.layers = [layer]
        else: self.layers = foldername_BBIP_SCAN
        self.date = date
        
    def _get_data_path(self, layer: str) -> str:
        """Gets the full folder path according to the layer."""
        if layer == LayerName.BORDE:
            return DataPath.SCAN_DATA_BORDE
        elif layer == LayerName.BRAS:
            return DataPath.SCAN_DATA_BRAS
        elif layer == LayerName.CACHING:
            return DataPath.SCAN_DATA_CACHING
        elif layer == LayerName.RAI:
            return DataPath.SCAN_DATA_RAI
        elif layer == LayerName.IXP:
            return DataPath.SCAN_DATA_IXP
        elif layer == LayerName.IP_BRAS:
            return DataPath.SCAN_DATA_IP_BRAS
        
    def _get_daily_path(self, layer: str) -> str:
        """Returns the complete folder path for daily summary data storage."""
        filename = os.path.join(self._folder_path, f"{layer}")
        return os.path.join(self._folder_path, filename)
            
    def _get_report(self, layer: str) -> pd.DataFrame:
        """Returns the data obtained from SCAN for a layer."""
        if layer == LayerName.IP_BRAS: columns = header_daily_ip_bras
        else: columns = header_daily_bbip
        filepath = self._get_daily_path(layer)
        if os.path.exists(filepath): 
            df = pd.read_csv(filepath, sep=self._separator_data, skiprows=1, names=columns)
        else:
            df = pd.DataFrame(columns=columns)
        return df
            
    def _calculate_summary_data(self, interface: str, type: str, capacity: float, data: pd.DataFrame) -> pd.DataFrame:
        """Returns the daily summary data of a BBIP layer."""
        try:
            data = data[data[HeaderBBIP.DATE] == self.date]
            if data.empty: return pd.DataFrame(columns=header_daily_bbip)
            in_average = (data[HeaderBBIP.IN_PROM].mean()) * FACTOR_BBIP
            out_average = (data[HeaderBBIP.OUT_PROM].mean()) * FACTOR_BBIP
            in_max_average = (float(data[HeaderBBIP.IN_MAX].max())) * FACTOR_BBIP
            out_max_average = (float(data[HeaderBBIP.OUT_MAX].max())) * FACTOR_BBIP
            if in_max_average >= out_max_average: use = (in_max_average / capacity) * 100
            else: use = (out_max_average / capacity) * 100
            summary_data = pd.DataFrame({
                HeaderDailySummary.NAME: [interface],
                HeaderDailySummary.TYPE: [type],
                HeaderDailySummary.DATE: [self.date],
                HeaderDailySummary.CAPACITY: [capacity],
                HeaderDailySummary.IN_PROM: [in_average],
                HeaderDailySummary.IN_MAX: [in_max_average],
                HeaderDailySummary.OUT_PROM: [out_average],
                HeaderDailySummary.OUT_MAX: [out_max_average],
                HeaderDailySummary.USE: [use]
            })
            return summary_data
        except Exception as error:
            log.error(f"Rutina resúmenes diarios. Fallo en cálculo de la data de BBIP de la interfaz: {interface} - {error}")
            return pd.DataFrame(columns=header_daily_bbip)
            
    def _calculate_summary_ip_data(self, interface: str, type: str, capacity: float, data: pd.DataFrame) -> pd.DataFrame:
        """Returns the daily summary data of IPBras layer."""
        try:
            data = data[data[HeaderIPBras.DATE] == self.date]
            if data.empty: return pd.DataFrame(columns=header_daily_bbip)
            in_average = round(data[HeaderIPBras.IN_PROM].mean())
            in_max_average = round(float(data[HeaderIPBras.IN_MAX].max()))
            summary_data = pd.DataFrame({
                HeaderIPBras.DATE: [self.date],
                HeaderIPBras.BRAS_NAME: [interface],
                HeaderIPBras.IN_PROM: [in_average],
                HeaderIPBras.IN_MAX: [in_max_average],
                HeaderIPBras.TYPE: [type],
                HeaderIPBras.CAPACITY: [capacity]
            })
            return summary_data
        except Exception as error:
            log.error(f"Rutina resúmenes diarios. Fallo en cálculo de la data de IPBras de la interfaz: {interface} - {error}")
            return pd.DataFrame(columns=header_daily_ip_bras)
    
    def run(self) -> None:
        """Executes the retrieval of daily layer summaries."""
        log.info("Inicio de generación de reportes diarios...")
        try:
            for layer in self.layers:
                folder_data = self._get_data_path(layer)
                if layer != LayerName.IP_BRAS: summary_report = pd.DataFrame(columns=header_daily_bbip)
                else: summary_report = pd.DataFrame(columns=header_daily_ip_bras)
                for filename in os.listdir(folder_data):
                    filepath = os.path.join(folder_data, filename)
                    name = filename.rsplit(self._separator_name)[1].replace("&", "/")
                    capacity = float(filename.split(self._separator_name)[-1])
                    type = filename.rsplit(self._separator_name)[0]
                    if layer != LayerName.IP_BRAS:
                        data = pd.read_csv(filepath, sep=self._separator_data, names=header_scan_bbip)
                        summary_data = self._calculate_summary_data(interface=name, type=type, capacity=capacity, data=data)
                    else: 
                        data = pd.read_csv(filepath, sep=self._separator_data, names=header_scan_ip_bras)
                        summary_data = self._calculate_summary_ip_data(interface=name, type=type, capacity=capacity, data=data)
                    if summary_data.empty: continue
                    if summary_report.empty: summary_report = summary_data
                    else: summary_report = pd.concat([summary_report, summary_data], axis=0)
                    summary_report.reset_index(drop=True, inplace=True)
                old_daily_report = self._get_report(layer)
                if not old_daily_report.empty and not summary_report.empty:
                    summary_report = pd.concat([old_daily_report, summary_report], axis=0)
                    summary_report.reset_index(drop=True, inplace=True)
                if not summary_report.empty: summary_report.to_csv(self._get_daily_path(layer), index=False, sep=self._separator_data, decimal=self._export_decimal)
        except Exception as error:
            log.error(f"Rutina resúmenes diarios. Generación de reportes diarios fallido. {error}")
        else:
            log.info("Rutina resúmenes diarios. Generación de reportes diarios finalizada")


@click.command(help="Genera el reporte diario de la data obtenida de SCAN")
@click.option("-d", "--date", type=str, required=False, help="Especifica la fecha para obtención de los datos para el resumen diario. \t Formato: YYYY-MM-DD. \t Por defecto, si no se especifica, se genera los reportes del día anterior al actual")
@click.option("-l", "--layer", type=click.Choice(foldername_BBIP_SCAN), required=False, help="Especifica la capa en la que se desea generar el resumen diario. \t Por defecto, si no se especifica, genera el resumen de todas las capas")
def generate_daily_summary(layer: str | None = None, date: str | None = None) -> None:
    if date: report = GenerateDailySummary(date=date, layer=layer)
    else: report = GenerateDailySummary(layer=layer)
    report.run()
    

if __name__ == "__main__":
    generate_daily_summary()