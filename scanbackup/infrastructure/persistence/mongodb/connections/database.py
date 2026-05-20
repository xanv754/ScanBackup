from typing import Any, Dict
from pathlib import Path
from pymongo import MongoClient
from pymongo.collection import Collection
from scanbackup.shared import (
    MongoDatabaseError,
    MongoConnectionError,
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoImportCollectionError,
    MongoExportCollectionError,
    DatabaseDataNotFoundError,
    DatabaseDataContentError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.collections.records.bbip.traffic import (
    BBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.records.bbip.ip import (
    IPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.sources.bbip.bbip import (
    BBIPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.sources.bbip.ip import (
    IPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.summaries.bbip.daily_traffic import (
    BBIPDailySummaryCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.summaries.bbip.daily_ip import (
    IPDailySummaryCollection,
)


class MongoDatabase:
    _client: MongoClient[Any]
    _name_db: str
    _uri: str
    connected: bool = False

    def __init__(self, uri: str) -> None:
        self._uri = uri
        self.open_connection(uri)

    def _check_collection(self, name: str) -> bool:
        """Check if the collection exists."""
        db = self._client[self._name_db]
        collection_list = db.list_collection_names()
        return name in collection_list

    def get_uri(self) -> str:
        """Get the URI database."""
        return self._uri

    def open_connection(self, uri: str | None = None) -> None:
        """Open a connection to the database.

        :param uri: URI database
        :type uri: str
        """
        try:
            if not self.connected:
                if not uri:
                    uri = self._uri
                name_db = uri.split("/")[-1]
                self._name_db = name_db
                self._client = MongoClient(uri)
        except Exception as error:
            self.connected = False
            raise MongoConnectionError(error=error, extra_msg="Fallo al abrir conexión")
        else:
            self.connected = True

    def get_connection(self) -> MongoClient[Dict[str, Any]]:
        """Get a connection to the database.

        :return MongoClient[Any]: Client of MongoDB
        """
        return self._client

    def get_cursor(self, table: str | None = None) -> Collection[Any]:
        """Get a cursor to the database.

        :param table: Collection name
        :type table: str | None
        :return MongoClient[Any]: Connection in the database collection
        """
        if table:
            return self._client[self._name_db][table]
        else:
            return self._client[self._name_db].get_default_collection()

    def close_connection(self) -> None:
        """Close the connection to the database."""
        try:
            self._client.close()
            self.connected = False
        except Exception as error:
            raise MongoConnectionError(
                error=error, extra_msg="Fallo al cerrar conexión"
            )

    def initialize(self) -> None:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]
            if not self._check_collection(MongoCollectionName.BBIP_SOURCES):
                BBIPSourceCollection.create(database=db)
            if not self._check_collection(MongoCollectionName.BORDE):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.BORDE, database=db
                )
            if not self._check_collection(MongoCollectionName.BRAS):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.BRAS, database=db
                )
            if not self._check_collection(MongoCollectionName.CACHING):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.CACHING, database=db
                )
            if not self._check_collection(MongoCollectionName.RAI):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.RAI, database=db
                )
            if not self._check_collection(MongoCollectionName.IXP):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.IXP, database=db
                )
            if not self._check_collection(MongoCollectionName.DINT):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.DINT, database=db
                )
            if not self._check_collection(MongoCollectionName.DIST):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.DIST, database=db
                )
            if not self._check_collection(MongoCollectionName.BBIP_DAILY_SUMMARY):
                BBIPDailySummaryCollection.create(database=db)
            if not self._check_collection(MongoCollectionName.IP_SOURCES):
                IPSourceCollection.create(database=db)

            if not self._check_collection(MongoCollectionName.IP_BRAS):
                IPCollection.create(
                    name_collection=MongoCollectionName.IP_BRAS, database=db
                )
            if not self._check_collection(MongoCollectionName.IP_DAILY_SUMMARY):
                IPDailySummaryCollection.create(database=db)
            self.close_connection()
        except MongoCreateCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al crear colecciones"
            )

    def import_data(
        self,
        name_collection: MongoCollectionName,
        filepath: str,
        delimiter: str | None = None,
    ) -> None:
        filepath = Path(filepath)
        try:
            if not filepath.exists():
                raise DatabaseDataNotFoundError()
            if name_collection is BBIPCollection.LAYERS_VALID:
                BBIPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection is IPCollection.LAYERS_VALID:
                IPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_SOURCES:
                BBIPSourceCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_SOURCES:
                IPSourceCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY:
                BBIPDailySummaryCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_DAILY_SUMMARY:
                IPDailySummaryCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            else:
                raise ValueError("Nombre de colección inválido")
        except MongoImportCollectionError:
            raise
        except DatabaseDataContentError:
            raise
        except DatabaseDataNotFoundError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al importar la data"
            )

    def export_data(
        self,
        filepath: str | None = None,
        name_collection: MongoCollectionName | None = None,
        delimiter: str | None = None,
        include_id: bool = True,
    ) -> None:
        if not filepath:
            filepath = Path.home()
        else:
            filepath = Path(filepath)
        try:
            if not name_collection or name_collection == MongoCollectionName.BORDE:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.BORDE,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.BORDE}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.BRAS:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.BRAS,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.BRAS}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.CACHING:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.CACHING,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.CACHING}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.RAI:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.RAI,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.RAI}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.DINT:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.DINT,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.DINT}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.DIST:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.DIST,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.DIST}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.IXP:
                BBIPCollection.export_data(
                    name_collection=MongoCollectionName.IXP,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.IXP}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.IP_BRAS:
                IPCollection.export_data(
                    name_collection=MongoCollectionName.IP_BRAS,
                    database=self._client,
                    output_path=Path(filepath / f"{MongoCollectionName.IP_BRAS}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if (
                not name_collection
                or name_collection == MongoCollectionName.BBIP_SOURCES
            ):
                BBIPSourceCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        filepath / f"{MongoCollectionName.BBIP_SOURCES}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if not name_collection or name_collection == MongoCollectionName.IP_SOURCES:
                IPSourceCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        filepath / f"{MongoCollectionName.IP_SOURCES}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if (
                not name_collection
                or name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY
            ):
                BBIPDailySummaryCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        filepath / f"{MongoCollectionName.BBIP_DAILY_SUMMARY}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            if (
                not name_collection
                or name_collection == MongoCollectionName.IP_DAILY_SUMMARY
            ):
                IPDailySummaryCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        filepath / f"{MongoCollectionName.IP_DAILY_SUMMARY}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            else:
                raise ValueError("Nombre de colección inválido")
        except MongoExportCollectionError:
            raise
        except ValueError:
            if name_collection:
                raise MongoExportCollectionError(
                    name=name_collection, extra_msg="Nombre de la colección desconocido"
                )
            else:
                raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al importar la data"
            )

    def drop(self, force: bool = False) -> None:
        """Deletes all collections in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]

            if not force:
                self.export_data()

            BBIPCollection.delete(MongoCollectionName.BORDE, db)
            BBIPCollection.delete(MongoCollectionName.BRAS, db)
            BBIPCollection.delete(MongoCollectionName.CACHING, db)
            BBIPCollection.delete(MongoCollectionName.RAI, db)
            BBIPCollection.delete(MongoCollectionName.DINT, db)
            BBIPCollection.delete(MongoCollectionName.DIST, db)
            BBIPCollection.delete(MongoCollectionName.IXP, db)
            BBIPDailySummaryCollection.delete(db)
            BBIPSourceCollection.delete(db)

            IPCollection.delete(MongoCollectionName.IP_BRAS, db)
            IPDailySummaryCollection.delete(db)
            IPSourceCollection.delete(db)
            self.close_connection()
        except MongoExportCollectionError:
            raise
        except MongoDeleteCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al eliminar colecciones"
            )
