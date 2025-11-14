import os
import pandas as pd
from datetime import datetime, timedelta
from scanbackup.constants import HeaderIPBras, LayerName, header_scan_ip_bras
from scanbackup.database.querys.bbip.ipBras import IPBrasMongoQuery
from scanbackup.model import IPBrasModel
from scanbackup.utils import LayerDetector, log


class IPHistoryUpdaterHandler:
    """IP History data updater handler."""

    _date: str
    _force: bool = False

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
            df_to_upload = pd.DataFrame(columns=header_scan_ip_bras)
            subdirs = [d for d in os.listdir(folderpath)]
            for subdir in subdirs:
                subdir_path = os.path.join(folderpath, subdir)
                brasname = subdir.split("%")[1].strip() if "%" in subdir else subdir
                try:
                    file_path = subdir_path
                    brasname = file_path.split("/")[-1]
                    df_data = pd.read_csv(
                        file_path, sep=" ", header=None, names=header_scan_ip_bras
                    )
                    df_data = df_data.dropna(
                        subset=[
                            HeaderIPBras.DATE,
                            HeaderIPBras.TIME,
                            HeaderIPBras.IN_PROM,
                        ]
                    )  # No requerir inMax si es opcional
                    if not force:
                        df_data = df_data[df_data[HeaderIPBras.DATE] == date]
                    if not df_data.empty:
                        df_data[HeaderIPBras.BRAS_NAME] = brasname
                        if df_to_upload.empty:
                            df_to_upload = df_data
                        else:
                            df_to_upload = pd.concat([df_to_upload, df_data], axis=0)
                except Exception as error:
                    log.error(f"Ha ocurrido un error al cargar la data del archivo: {brasname} - {error}")
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
                log.warning(f"IPBRAS: Data vacía obtenida")
                return True
            chunk_size = 1000
            query = IPBrasMongoQuery(uri=uri)
            from scanbackup.constants import TableName

            for i in range(0, len(data), chunk_size):
                chunk = data.iloc[i : i + chunk_size]
                data_json = chunk.to_dict(orient="records")
                try:
                    json = [IPBrasModel(**item) for item in data_json]
                except Exception as error:
                    log.error(
                        f"BBIP Updater. IPBRAS: Fallo al validar los data de la capa contra el modelo. El sistema de actualización para la capa se ha suspendido"
                    )
                    return False
                response = query.new_interface(TableName.IP_BRAS_HISTORY, json)
                if not response: raise Exception()
            self._clean_data()
            return True
        except Exception as error:
            log.error(f"BBIP Updater. IPBRAS: Fallo al cargar los datos de la capa en la base de datos - {error}")
            return False

    def _clean_data(self) -> None:
        """Clears all files in IPBras that have been successfully updated."""
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.IP_BRAS)
            subdirs = [
                d
                for d in os.listdir(folderpath)
                if os.path.isdir(os.path.join(folderpath, d))
            ]
            for subdir in subdirs:
                subdir_path = os.path.join(folderpath, subdir)
                files = [
                    f
                    for f in os.listdir(subdir_path)
                    if os.path.isfile(os.path.join(subdir_path, f))
                ]
                for brasname in files:
                    if not self._force:
                        df_data = pd.read_csv(
                            os.path.join(subdir_path, brasname),
                            sep=" ",
                            header=None,
                            names=header_scan_ip_bras,
                        )
                        df_data = df_data[df_data[HeaderIPBras.DATE] != self._date]
                        if not df_data.empty:
                            df_data = df_data.reset_index(drop=True)
                            df_data.to_csv(
                                os.path.join(subdir_path, brasname),
                                sep=" ",
                                index=False,
                            )
                            continue
                    os.remove(os.path.join(subdir_path, brasname))
        except Exception as error:
            log.error(f"BBIP Updater. IPBRAS: Fallo al limpiar los archivos de la capa - {error}")
