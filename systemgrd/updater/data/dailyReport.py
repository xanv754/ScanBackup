import os
import pandas as pd
from datetime import datetime, timedelta
from systemgrd.constants import (
    LayerName,
    HeaderDailyReport,
    HeaderBBIP,
    HeaderIPBras,
    header_daily,
    header_daily_bbip,
    header_daily_ip_bras
)
from systemgrd.database import DailyReportMongoQuery
from systemgrd.model import DailyReportModel
from systemgrd.utils import LayerDetector, log


class DailyReportUpdaterHandler:
    """Daily report data updater handler."""

    _separator: str = " "
    _date: str
    _force: bool = False

    def _get_summary(
        self, path: str, data_upload: pd.DataFrame, date: str, force: bool
    ) -> pd.DataFrame:
        """Read all summary daily of a layer specified through a path."""
        filename = os.path.basename(path)
        layer = filename.upper().strip()
        df = pd.read_csv(path, sep=self._separator, names=header_daily_bbip, index_col=False, skiprows=1)  # type: ignore
        if not force:
            df = df[df[HeaderDailyReport.DATE] == date]
        if not df.empty:
            df[HeaderDailyReport.TYPE_LAYER] = layer
            if data_upload.empty:
                data_upload = df
            else:
                data_upload = pd.concat([data_upload, df], axis=0)
        return data_upload

    def _clean_data(self) -> None:
        """Clears all files in a layer that have been successfully updated."""
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.DAILY_REPORT)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                if not self._force:
                    if filename != LayerName.IP_BRAS:
                        df_data = pd.read_csv(os.path.join(folderpath, filename), sep=self._separator, header=None, names=header_daily_bbip, skiprows=1)  # type: ignore
                        df_data = df_data[df_data[HeaderBBIP.DATE] != self._date]
                    else:
                        df_data = pd.read_csv(os.path.join(folderpath, filename), sep=self._separator, header=None, names=header_daily_ip_bras, skiprows=1)  # type: ignore
                        df_data = df_data[df_data[HeaderIPBras.DATE] != self._date]
                    if not df_data.empty:
                        df_data.to_csv(os.path.join(folderpath, filename), sep=self._separator)
                        continue
                os.remove(os.path.join(folderpath, filename))
        except Exception as error:
            log.error(f"Daily Report Updater. Fallo al limpiar la data de los reportes diarios - {error}")

    def get_data(self, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.DAILY_REPORT)
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
                    log.error(f"Ha ocurrido un error al cargar la data del archivo: {filename} - {error}")
                    continue
        except Exception as error:
            log.error(f"Daily Report Updater. Fallo al obtener la data de los reportes diarios - {error}")
            return pd.DataFrame(columns=header_daily)
        else:
            self._date = date
            self._force = force
            return df_data

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty:
                log.warning(f"El sistema no encontró data en los reportes diarios para actualizar la base de datos")
                return False
            query = DailyReportMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")  # type: ignore
            try:
                json = [DailyReportModel(**item) for item in data_json]  # type: ignore
            except Exception as error:
                log.error(
                    f"Fallo al validar los data de los reportes diarios contra el modelo. El sistema de actualización de los reportes diarios se ha suspendido - {error}"
                )
                return False
            else:
                response = query.new_report(json)
                if response:
                    self._clean_data()
                return response
        except Exception as error:
            log.error(f"Daily Report Updater. Fallo al cargar los datos de los reportes diarios en la base de datos - {error}")
            return False
