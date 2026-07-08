import json
from pathlib import Path
from datetime import date
from scanbackup.domain import (
    TrafficHistoryBBIPRepository,
    TrafficSourceBBIPRepository,
    TrafficDailySummaryBBIPRepository,
    TrafficBBIPEntity,
)
from scanbackup.shared import (
    Configuration,
    SCANHeader,
    TrafficHistoryBBIPHeader,
    DataNotFoundError,
    ContentFileError,
    UpdaterError,
    Log,
)
from scanbackup.application.use_case.bbip.updaters.daily_summary_traffic import (
    TrafficDailySummaryUpdaterUseCase,
)
import pandas as pd


class TrafficHistoryUpdaterUseCase:
    _layer: str
    _repo_history: TrafficHistoryBBIPRepository
    _repo_sources: TrafficSourceBBIPRepository
    _repo_daily: TrafficDailySummaryBBIPRepository
    _date: date

    def __init__(
        self,
        layer: str,
        history_repository: TrafficHistoryBBIPRepository,
        source_repository: TrafficSourceBBIPRepository,
        daily_repository: TrafficDailySummaryBBIPRepository,
        data_date: str,
    ) -> None:
        self._layer = layer
        self._repo_history = history_repository
        self._repo_sources = source_repository
        self._repo_daily = daily_repository
        date_format = date.fromisoformat(data_date)
        self._date = date_format

    def _get_config_variables(self) -> tuple[Path, str, str]:
        system = Configuration()
        homepath = system.get_projectpath()
        config_metada = system.get_cfg_metadata()
        base_folder = config_metada.dir_data
        traffic_folder = config_metada.scanner.dir_storage
        dirpath = Path(homepath) / base_folder / traffic_folder
        if not dirpath.is_dir():
            raise DataNotFoundError(dirpath.resolve())

        data_delimiter = config_metada.scanner.file_delimiter
        data_date_format = config_metada.scanner.date_format
        search_date = self._date.strftime(data_date_format)

        return dirpath, data_delimiter, search_date

    def _valid_data_file(
        self, header_line: str, data_delimiter: str
    ) -> tuple[bool, set[str], set[str]]:
        header_expected = {header.value for header in SCANHeader}
        header_actual = {col.strip() for col in header_line.split(data_delimiter)}

        return (
            header_expected == header_actual,
            header_expected - header_actual,
            header_actual - header_expected,
        )

    def _get_data_file(
        self, files: list[str], data_delimiter: str, filter_date: str
    ) -> pd.DataFrame:
        data_upload = pd.DataFrame(columns=[header.value for header in SCANHeader])
        for file in files:
            with open(file) as f:
                try:
                    header_line = f.readline().strip()
                    is_valid_data, missing, extra = self._valid_data_file(
                        header_line, data_delimiter
                    )
                    if not is_valid_data:
                        raise ContentFileError(
                            file,
                            message=f"Encabezados del archivo faltantes: {missing}, encabezados del archivo sobrantes: {extra}",
                        )
                except:
                    continue

                data = pd.read_csv(file, sep=data_delimiter)
                data = data[data[SCANHeader.DATE.value] == filter_date]
                if data.empty:
                    Log.warning(
                        f"No encontró data del {filter_date} en el archivo {file}. Data skipping..."
                    )
                    continue

                data_upload = pd.concat([data_upload, data])
        data_upload.columns = data_upload.columns.str.upper()
        return data_upload

    def _get_sources(self) -> pd.DataFrame:
        sources = self._repo_sources.get_sources_by_layer_id(self._layer)
        data_sources = pd.DataFrame([s.model_dump() for s in sources])
        data_sources.columns = data_sources.columns.str.upper()
        return data_sources

    def _merge_info(self, data: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
        merge_data = pd.merge(
            data,
            sources,
            how="inner",
            on=[SCANHeader.INTERFACE.value.upper()],
            suffixes=("", "_y"),
        )
        merge_data = merge_data[
            [header.value.upper() for header in TrafficHistoryBBIPHeader]
        ]
        merge_data = merge_data[
            [
                TrafficHistoryBBIPHeader.DATE.value.upper(),
                TrafficHistoryBBIPHeader.TIME.value.upper(),
                TrafficHistoryBBIPHeader.IN_PROM.value.upper(),
                TrafficHistoryBBIPHeader.IN_MAX.value.upper(),
                TrafficHistoryBBIPHeader.OUT_PROM.value.upper(),
                TrafficHistoryBBIPHeader.OUT_MAX.value.upper(),
                TrafficHistoryBBIPHeader.DEVICE.value.upper(),
            ]
        ]
        merge_data.columns = merge_data.columns.str.lower()
        return merge_data

    def execute(self) -> None:
        try:
            dirpath, data_delimiter, filter_date = self._get_config_variables()

            files = [
                str(file.as_posix()) for file in dirpath.iterdir() if file.is_file()
            ]
            data_upload = self._get_data_file(files, data_delimiter, filter_date)

            if not data_upload.empty:
                data_sources = self._get_sources()

                daily_summary_use_case = TrafficDailySummaryUpdaterUseCase(
                    self._repo_daily
                )
                daily_summary_use_case.execute(data_upload.copy(), data_sources.copy())

                merge_data = self._merge_info(data_upload, data_sources)

                data_json = merge_data.to_json(orient="records")
                records = json.loads(data_json)

                entities: list[TrafficBBIPEntity] = [
                    TrafficBBIPEntity(**record) for record in records
                ]

                self._repo_history.insert(entities)
        except DataNotFoundError:
            raise
        except Exception as error:
            raise UpdaterError(
                message=f"Error al actualizar los datos históricos de la capa {self._layer}",
                error=error,
            )
