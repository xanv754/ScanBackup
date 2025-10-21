import os
import pandas as pd
from datetime import datetime, timedelta
from systemgrd.constants import (
    LayerName,
    HeaderDailyReport,
    HeaderBBIP,
    header_daily_report,
    header_upload_daily_data,
)
from systemgrd.database import DailyReportMongoQuery
from systemgrd.model import DailyReportModel
from systemgrd.utils import LayerDetector, log


class DailyReportUpdaterHandler:
    """Daily report data updater handler."""

    _date: str
    _force: bool = False

    def _get_summary(
        self, path: str, data_upload: pd.DataFrame, date: str, force: bool
    ) -> pd.DataFrame:
        """Read all summary daily of a layer specified through a path."""
        filename = os.path.basename(path)
        layer = filename.replace(".", "_").split("_")[1].upper().strip()
        df = pd.read_csv(path, sep=" ", names=header_upload_daily_data, index_col=False, skiprows=1)  # type: ignore
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
                    df_data = pd.read_csv(os.path.join(folderpath, filename), sep=" ", header=None, names=header_upload_daily_data, skiprows=1)  # type: ignore
                    df_data = df_data[df_data[HeaderBBIP.DATE] != self._date]
                    if not df_data.empty:
                        df_data.to_csv(os.path.join(folderpath, filename), sep=" ")
                        continue
                os.remove(os.path.join(folderpath, filename))
        except Exception as e:
            log.error(f"Failed to data clean data file of daily reports layer. {e}")

    def get_data(self, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            folderpath = LayerDetector.get_folder_path(layer=LayerName.DAILY_REPORT)
            if not date:
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_data = pd.DataFrame(columns=header_daily_report)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                try:
                    df_data = self._get_summary(
                        path=f"{folderpath}/{filename}",
                        data_upload=df_data,
                        date=date,
                        force=force,
                    )
                except Exception as e:
                    log.error(f"Something went wrong to get data: {filename}. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to get data of daily report. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            self._date = date
            self._force = force
            return df_data

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty:
                log.warning(
                    "The system received empty data daily report when it updated."
                )
                return False
            query = DailyReportMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")  # type: ignore
            try:
                json = [DailyReportModel(**item) for item in data_json]  # type: ignore
            except Exception as e:
                log.error(
                    f"Failed to validate data with the model. Daily report updater system has suspended. {e}"
                )
                return False
            else:
                response = query.new_report(json)
                if response:
                    self._clean_data()
                return response
        except Exception as e:
            log.error(f"Failed to load data of daily report. {e}")
            return False
