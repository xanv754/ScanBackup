import os
import pandas as pd
from datetime import datetime, timedelta
from scanbackup.constants import (
    LayerName,
    HeaderDailySummary,
    HeaderBBIP,
    HeaderIPBras,
    header_daily,
    header_daily_bbip,
    header_daily_ip_bras,
)
from scanbackup.database import DailySummaryMongoQuery
from scanbackup.model import DailySummaryModel
from scanbackup.utils import LayerDetector, log


class DailySummaryUpdaterHandler:
    """Daily summary data updater handler."""

    _separator: str = ";"
    _date: str
    _force: bool = False

    def _get_summary(
        self, path: str, data_upload: pd.DataFrame, date: str, force: bool
    ) -> pd.DataFrame:
        """Read all summary daily of a layer specified through a path."""
        filename = os.path.basename(path)
        layer = filename.split("/")[-1].upper().strip()
        if layer != LayerName.IP_BRAS: df = pd.read_csv(path, sep=self._separator, names=header_daily_bbip, index_col=False, skiprows=1)
        else:
            df = pd.read_csv(path, sep=self._separator, names=header_daily_ip_bras, index_col=False, skiprows=1)
            df[HeaderBBIP.OUT_MAX] = 0
            df[HeaderBBIP.OUT_PROM] = 0
            df[HeaderDailySummary.USE] = 0
            df[HeaderBBIP.TYPE] = LayerName.IP_BRAS
            df.rename(columns={HeaderIPBras.BRAS_NAME: HeaderBBIP.NAME}, inplace=True)
        if not force: df = df[df[HeaderDailySummary.DATE] == date]
        if not df.empty:
            df[HeaderDailySummary.TYPE_LAYER] = layer
            if data_upload.empty: data_upload = df
            else: data_upload = pd.concat([data_upload, df], axis=0)
        return data_upload

    def _clean_data(self) -> None:
        """Clears all files in a layer that have been successfully updated."""
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.DAILY_SUMMARY)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                if not self._force:
                    if filename != LayerName.IP_BRAS:
                        df_data = pd.read_csv(os.path.join(folderpath, filename), sep=self._separator, header=None, names=header_daily_bbip, skiprows=1)
                        df_data = df_data[df_data[HeaderBBIP.DATE] != self._date]
                    else:
                        df_data = pd.read_csv(os.path.join(folderpath, filename), sep=self._separator, header=None, names=header_daily_ip_bras, skiprows=1)
                        df_data = df_data[df_data[HeaderIPBras.DATE] != self._date]
                    if not df_data.empty:
                        df_data.to_csv(os.path.join(folderpath, filename), sep=self._separator)
                        continue
                os.remove(os.path.join(folderpath, filename))
        except Exception as error:
            log.error(f"Daily Summary Updater. DAILY SUMMARY: Fallo al limpiar los archivos de la capa - {error}")

    def get_data(self, date: str | None = None, force: bool = False) -> pd.DataFrame:
        """Get data to be loaded in the database.

        :params date: Date to be used for filtering.
        :type date: str | None
        :params force: If this is true, as much data as possible will be uploaded, regardless of the dates.
        :type force: bool. Default False
        :returns DataFrame: Data to save in database.
        """
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.DAILY_SUMMARY)
            if not date:
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_data = pd.DataFrame(columns=header_daily)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                try:
                    df_data = self._get_summary(
                        path=os.path.join(folderpath, filename),
                        data_upload=df_data,
                        date=date,
                        force=force,
                    )
                except Exception as error:
                    log.error(f"Daily Summary Updater. DAILY SUMMARY: Ha ocurrido un error al cargar la data del archivo: {filename} - {error}")
                    continue
            if not df_data.empty: 
                df_data = df_data.drop_duplicates(
                    subset=[
                        HeaderDailySummary.NAME, HeaderDailySummary.DATE, 
                        HeaderDailySummary.CAPACITY, HeaderDailySummary.TYPE_LAYER, 
                        HeaderDailySummary.TYPE
                    ], 
                    keep="first"
                )
        except Exception as error:
            log.error(f"Daily Summary Updater. DAILY SUMMARY: Fallo al obtener la data de los resúmenes diarios - {error}")
            return pd.DataFrame(columns=header_daily)
        else:
            self._date = date
            self._force = force
            return df_data

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        """Load data in the database.

        :params data: Data to be loaded.
        :type data: DataFrame
        :params uri: URI to connect to the database.
        :type uri: str
        :returns bool: True if the data was saved successfully, otherwise False.
        """
        try:
            if data.empty:
                log.warning(f"DAILY SUMMARY: Data vacía obtenida")
                return False
            query = DailySummaryMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [DailySummaryModel(**item) for item in data_json]
            except Exception as error:
                log.error(
                    f"BBIP Updater. DAILY SUMMARY: Fallo al validar los data de los resúmenes diarios contra el modelo. El sistema de actualización se ha suspendido - {error}"
                )
                return False
            else:
                response = query.new_report(json)
                if response:
                    self._clean_data()
                return response
        except Exception as error:
            log.error(f"Daily Summary Updater. DAILY SUMMARY: Fallo al cargar los datos de los resúmenes diarios en la base de datos - {error}")
            return False
