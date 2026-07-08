from typing import List
from pandas import DataFrame
from scanbackup.constants import TableName, IPBrasFieldName, header_ip_bras
from scanbackup.database.libs.database import DatabaseMongo
from scanbackup.database.utils.adapter import IPBrasResponseAdapter
from scanbackup.model import IPBrasModel
from scanbackup.utils import log, URIEnvironment


class IPBrasMongoQuery:
    """Mongo query class for IP Bras history table."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            if not uri:
                config = URIEnvironment(dev=dev)
                uri = config.get_uri_db()
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as error:
            log.error(
                f"Fallo al intentar conectarse a la base de datos del sistema - {error}"
            )

    def new_bras(self, data: List[IPBrasModel]) -> bool:
        """Register new data of IP bras.

        :param data: List of new bras of IP Bras to register.
        :type data: List[IPBrasModel]
        :return bool: Insertion status. If True, the interface has been registered correctly. Otherwise returns False.
        """
        try:
            status_insert = False
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS)
                response = cursor.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self._database.close_connection()
        except Exception as error:
            log.error(
                f"Fallo al registrar las nuevas interfaces en la colección: {TableName.IP_BRAS} - {error}"
            )
            return False
        else:
            return status_insert

    def get_bras(self, brasname: str) -> DataFrame:
        """Gets data of IP Bras of a bras.

        :param brasname: Name of the interface
        :type brasname: str
        :return DataFrame: Data obtained from the query
        """
        try:
            data: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS)
                result = cursor.find_one({IPBrasFieldName.BRAS_NAME: brasname})
                if result:
                    data = IPBrasResponseAdapter.to_dataframe([result])
                self._database.close_connection()
            return data
        except Exception as error:
            log.error(
                f"Fallo al intentar obtener la data de IP del agregador: {brasname} - {error}"
            )
            return DataFrame(columns=header_ip_bras)

    def get_all_bras(self) -> DataFrame:
        """Gets data of IP Bras of all bras.

        :return DataFrame: Data obtained from the query
        """
        try:
            data: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS)
                cursor = cursor.find()
                data = IPBrasResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return data
        except Exception as error:
            log.error(
                f"Fallo al intentar obtener toda la data de IP de los agregadores - {error}"
            )
            return DataFrame(columns=header_ip_bras)

    def get_bras_by_date(self, date: str) -> DataFrame:
        """Gets all data of IP Bras of all bras filtered by a date.

        :param date: Date of the data. Format: YYYY-MM-DD
        :type date: str
        :return DataFrame: Data obtained from the query
        """
        try:
            data: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS)
                cursor = cursor.find({IPBrasFieldName.DATE: date})
                data = IPBrasResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return data
        except Exception as error:
            log.error(
                f"Fallo al intentar obtener toda data de IP de los agregadores filtrado por el día {date} - {error}"
            )
            return DataFrame(columns=header_ip_bras)
