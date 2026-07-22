from abc import ABC, abstractmethod
from pathlib import Path
from scanbackup.shared import DatabaseConfigModel, LayerConfigModel


class BaseDatabase(ABC):
    @abstractmethod
    def set_uri(self, config: DatabaseConfigModel) -> None:
        pass

    @abstractmethod
    def create_collections(self, config: LayerConfigModel) -> None:
        pass

    @abstractmethod
    def import_data(
        self,
        name_collection: str,
        config: LayerConfigModel,
        input_filepath: str,
        delimiter: str,
    ) -> None:
        pass

    @abstractmethod
    def export_data(
        self,
        config: LayerConfigModel,
        name_collection: str,
        dirpath: Path | None = None,
        include_id: bool = True,
    ) -> str:
        pass

    @abstractmethod
    def get_collection_names(self) -> list[str]:
        pass
