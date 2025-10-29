import os
import pandas as pd
from datetime import datetime, timedelta
from systemgrd.constants import HeaderBBIP, header_bbip, header_scan_bbip
from systemgrd.database import BBIPMongoQuery
from systemgrd.model import BBIPModel
from systemgrd.utils import LayerDetector, log


class BBIPUpdaterHandler:
    """BBIP data updater handler."""

    _date: str
    _force: bool = False

    def _get_data_link(
        self, path: str, data_uploading: pd.DataFrame, date: str, force: bool
    ) -> pd.DataFrame:
        """Read all links in a layer specified through a path."""
        filename = os.path.basename(path)
        type = filename.split("%")[0]
        interface = filename.split("%")[1]
        capacity = filename.split("%")[2]
        df_data = pd.read_csv(path, sep=" ", header=None, names=header_scan_bbip)  # type: ignore
        if not force:
            df_data = df_data[df_data[HeaderBBIP.DATE] == date]
        if not df_data.empty:
            df_data[HeaderBBIP.NAME] = interface
            df_data[HeaderBBIP.CAPACITY] = capacity
            df_data[HeaderBBIP.TYPE] = type
            if data_uploading.empty:
                data_uploading = df_data
            else:
                data_uploading = pd.concat([data_uploading, df_data], axis=0)
        return data_uploading

    def _clean_data(self, layer: str) -> None:
        """Clears all files in a layer that have been successfully updated."""
        try:
            folderpath = LayerDetector.get_folder_path(layer=layer)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                if not self._force:
                    df_data = pd.read_csv(os.path.join(folderpath, filename), sep=" ", header=None, names=header_scan_bbip)  # type: ignore
                    df_data = df_data[df_data[HeaderBBIP.DATE] != self._date]
                    if not df_data.empty:
                        df_data = df_data.reset_index(drop=True)
                        df_data.to_csv(os.path.join(folderpath, filename), sep=" ")
                        continue
                os.remove(os.path.join(folderpath, filename))
        except Exception as e:
            log.error(f"Failed to data clean data file of {layer} layer. {e}")

    def get_data(
        self, layer: str, date: str | None = None, force: bool = False
    ) -> pd.DataFrame:
        """Get data to be loaded in the database.

        :params layer: Layer name to update.
        :type layer: str
        :params date: Date to be used for filtering.
        :type date: str | None
        :params force: If this is true, as much data as possible will be uploaded, regardless of the dates.
        :type force: bool. Default False
        :returns DataFrame: Data to save in database.
        """
        try:
            folderpath = LayerDetector.get_folder_path(layer=layer)
            if not date:
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            files = [filename for filename in os.listdir(folderpath)]
            df_to_upload = pd.DataFrame(columns=header_scan_bbip)
            for filename in files:
                try:
                    df_to_upload = self._get_data_link(
                        path=os.path.join(folderpath, filename),
                        data_uploading=df_to_upload,
                        date=date,
                        force=force,
                    )
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to data load of {layer} layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            self._date = date
            self._force = force
            return df_to_upload

    def load_data(self, layer: str, data: pd.DataFrame, uri: str) -> bool:
        """Load data in the database.

        :params layer: Layer name to update.
        :type layer: str
        :params data: Data to be loaded.
        :type data: DataFrame
        :params uri: URI to connect to the database.
        :type uri: str
        :returns bool: True if the data was saved successfully, otherwise False.
        """
        try:
            if data.empty:
                log.warning(f"The system received empty data {layer} when it updated.")
                return False
            query = BBIPMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")  # type: ignore
            try:
                json = [BBIPModel(**item) for item in data_json]  # type: ignore
            except Exception as e:
                log.error(
                    f"Failed to validate data with the model. {layer} updater system has suspended. {e}"
                )
                return False
            else:
                table_name = LayerDetector.get_table_name(layer)
                response = query.new_interface(table_name, json)
                if response:
                    self._clean_data(layer=layer)
                return response
        except Exception as e:
            log.error(f"Failed to load data of Borde layer. {e}")
            return False
