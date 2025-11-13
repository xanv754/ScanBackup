from typing import List
from pandas import DataFrame
from scanbackup.constants import BBIPFieldName, header_bbip
from scanbackup.database.libs.database import DatabaseMongo
from scanbackup.database.querys.bbip.query import BBIPQuery
from scanbackup.database.utils.adapter import BBIPResponseAdapter
from scanbackup.model import BBIPModel
from scanbackup.utils import log, URIEnvironment


class BBIPMongoQuery(BBIPQuery):
    """Mongo query class for all services of BBIP data."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            if not uri or dev:
                config = URIEnvironment(dev=dev)
                uri = config.get_uri_db()
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as error:
            log.error(f"Fallo al intentar conectarse a la base de datos del sistema - {error}")

    def new_interface(self, collection: str, data: List[BBIPModel]) -> bool:
        try:
            status_insert = False
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                response = cursor.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self._database.close_connection()
        except Exception as error:
            log.error(f"Fallo al registrar las nuevas interfaces en la colección: {collection} - {error}")
            return False
        else:
            return status_insert

    def get_interface(self, collection: str, name: str) -> DataFrame:
        try:
            interface: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                result = cursor.find_one({BBIPFieldName.NAME: name})
                if result:
                    data = BBIPResponseAdapter.to_dataframe([result])
                    if not data.empty:
                        interface = data
                self._database.close_connection()
            return interface
        except Exception as error:
            log.error(f"Fallo al intentar obtener una interfaz de la colección: {collection} - {error}")
            return DataFrame(columns=header_bbip)

    def get_interfaces(self, collection: str) -> DataFrame:
        try:
            interfaces: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                cursor = cursor.find()
                interfaces = BBIPResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return interfaces
        except Exception as error:
            log.error(f"Fallo al intentar obtener todas las interfaces de la colección: {collection} - {error}")
            return DataFrame(columns=header_bbip)

    def get_interfaces_by_date(self, collection: str, date: str) -> DataFrame:
        try:
            interfaces: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                cursor = cursor.find({BBIPFieldName.DATE: date})
                interfaces = BBIPResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return interfaces
        except Exception as error:
            log.error(f"Fallo al intentar obtener las interfaces de la colección: {collection} del día: {date} - {error}")
            return DataFrame(columns=header_bbip)
