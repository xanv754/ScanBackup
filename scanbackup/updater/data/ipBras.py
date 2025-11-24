import os
import pandas as pd
from datetime import datetime, timedelta
from scanbackup.constants import HeaderIPBras, LayerName, header_scan_ip_bras
from scanbackup.database.querys.bbip.ipBras import IPBrasMongoQuery
from scanbackup.model import IPBrasModel
from scanbackup.utils import LayerDetector, log


class IPBrasUpdaterHandler:
    """IP History data updater handler."""

    _date: str
    _force: bool = False
    _separator_data: str = ";"
    _separator_name: str = ";"
    
    def _get_data_information(
        self, path: str, data_uploading: pd.DataFrame, date: str, force: bool
    ) -> pd.DataFrame:
        """Read all data in a layer specified through a path."""
        filename = os.path.basename(path)
        capacity = filename.split(self._separator_name)[0]
        bras = filename.split(self._separator_name)[1]
        df_data = pd.read_csv(path, sep=self._separator_data, header=None, names=header_scan_ip_bras)
        if not force: df_data = df_data[df_data[HeaderIPBras.DATE] == date]
        if not df_data.empty:
            df_data[HeaderIPBras.BRAS_NAME] = bras
            df_data[HeaderIPBras.CAPACITY] = capacity
            if data_uploading.empty:
                data_uploading = df_data
            else:
                data_uploading = pd.concat([data_uploading, df_data], axis=0)
        return data_uploading

    def _clean_data(self) -> None:
        """Clears all files in a layer that have been successfully updated."""
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.IP_BRAS)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                if not self._force:
                    df_data = pd.read_csv(os.path.join(folderpath, filename), sep=self._separator_data, header=None, names=header_scan_ip_bras)
                    df_data = df_data[df_data[HeaderIPBras.DATE] != self._date]
                    if not df_data.empty:
                        df_data = df_data.reset_index(drop=True)
                        df_data.to_csv(os.path.join(folderpath, filename), sep=self._separator_data)
                        continue
                os.remove(os.path.join(folderpath, filename))
        except Exception as error:
            log.error(f"BBIP Updater. {LayerName.IP_BRAS}: Fallo al limpiar los archivos de la capa - {error}")


    def get_data(self, date: str | None = None, force: bool = False) -> pd.DataFrame:
        """Get data to be loaded in the database.

        :params date: Date to be used for filtering.
        :type date: str | None
        :params force: If this is true, as much data as possible will be uploaded, regardless of the dates.
        :type force: bool. Default False
        :returns DataFrame: Data to save in database.
        """
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.IP_BRAS)
            if not date:
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            files = [filename for filename in os.listdir(folderpath)]
            df_to_upload = pd.DataFrame(columns=header_scan_ip_bras)
            for filename in files:
                try:
                    df_to_upload = self._get_data_information(
                        path=os.path.join(folderpath, filename),
                        data_uploading=df_to_upload,
                        date=date,
                        force=force,
                    )
                except Exception as error:
                    log.error(f"Ha ocurrido un error al cargar la data del archivo: {filename} - {error}")
                    continue
        except Exception as error:
            log.error(f"BBIP Updater. IPBRAS: Fallo al cargar la data de la capa - {error}")
            return pd.DataFrame(columns=header_scan_ip_bras)
        else:
            self._date = date
            self._force = force
            return df_to_upload

    def load_data(self, data: pd.DataFrame, uri: str) -> bool:
        """Load data in the database.

        :params data: Data to be loaded.
        :type data: DataFrame
        :params uri: URI to connect to the database.
        :type uri: str
        :returns bool: True if the data was saved successfully, otherwise False.
        """
        try:
            if data.empty:
                log.warning(f"{LayerName.IP_BRAS}: Data vacía obtenida")
                return True
            query = IPBrasMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [IPBrasModel(**item) for item in data_json]
            except Exception as error:
                log.error(
                    f"BBIP Updater. {LayerName.IP_BRAS}: Fallo al validar los data de la capa contra el modelo. El sistema de actualización para la capa se ha suspendido - {error}"
                )
                return False
            else:
                response = query.new_bras(json)
                if response: self._clean_data()
                return response
        except Exception as error:
            log.error(f"BBIP Updater. IPBRAS: Fallo al cargar los datos de la capa en la base de datos - {error}")
            return False