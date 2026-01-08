import pandas as pd
from datetime import timedelta, datetime
from scanbackup.constants import (
    LayerName,
    HeaderBBIP,
    header_all_bbip,
    header_daily,
)
from scanbackup.handler.bbip import BBIPHandler
from scanbackup.utils import Validate, log


class LayerHandler:
    """Class to get data of BBIP layer."""

    __error_connection: bool = False
    bbip_handler: BBIPHandler

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            self.bbip_handler = BBIPHandler(uri=uri, dev=dev)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo al intentarse conectarse a la base de datos del sistema - {error}"
            )
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interface data from the BBIP.

        :return DataFrame: BBIP data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            df_borde = self.bbip_handler.get_all_interfaces(LayerName.BORDE)
            df_borde[HeaderBBIP.TYPE_LAYER] = LayerName.BORDE
            df_bras = self.bbip_handler.get_all_interfaces(LayerName.BRAS)
            df_bras[HeaderBBIP.TYPE_LAYER] = LayerName.BRAS
            df_caching = self.bbip_handler.get_all_interfaces(LayerName.CACHING)
            df_caching[HeaderBBIP.TYPE_LAYER] = LayerName.CACHING
            df_rai = self.bbip_handler.get_all_interfaces(LayerName.RAI)
            df_rai[HeaderBBIP.TYPE_LAYER] = LayerName.RAI
            df_ixp = self.bbip_handler.get_all_interfaces(LayerName.IXP)
            df_ixp[HeaderBBIP.TYPE_LAYER] = LayerName.IXP
            data = [
                df
                for df in [df_borde, df_bras, df_caching, df_rai, df_ixp]
                if not df.empty
            ]
            df_interfaces = pd.concat(data, axis=0)
            if data:
                df_interfaces = pd.concat(data, axis=0)
                df_interfaces.drop_duplicates(inplace=True)
                df_interfaces.reset_index(drop=True, inplace=True)
                return df_interfaces
            else:
                return pd.DataFrame(columns=header_all_bbip)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todas las interfaces del BBIP - {error}"
            )
            return pd.DataFrame(columns=header_all_bbip)

    def get_all_interfaces_by_date(self, date: str) -> pd.DataFrame:
        """Get all interface data from the BBIP filtered by a specific date.

        :param date: Date to filter by. Format: YYYY-MM-DD.
        :type date: str
        :return DataFrame: BBIP data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            if not Validate.date(date):
                raise Exception("Fecha no válida")
            df_borde = self.bbip_handler.get_all_interfaces_by_date(
                layer=LayerName.BORDE, date=date
            )
            df_borde[HeaderBBIP.TYPE_LAYER] = LayerName.BORDE
            df_bras = self.bbip_handler.get_all_interfaces_by_date(
                layer=LayerName.BRAS, date=date
            )
            df_bras[HeaderBBIP.TYPE_LAYER] = LayerName.BRAS
            df_caching = self.bbip_handler.get_all_interfaces_by_date(
                layer=LayerName.CACHING, date=date
            )
            df_caching[HeaderBBIP.TYPE_LAYER] = LayerName.CACHING
            df_rai = self.bbip_handler.get_all_interfaces_by_date(
                layer=LayerName.RAI, date=date
            )
            df_rai[HeaderBBIP.TYPE_LAYER] = LayerName.RAI
            df_ixp = self.bbip_handler.get_all_interfaces_by_date(
                layer=LayerName.IXP, date=date
            )
            df_ixp[HeaderBBIP.TYPE_LAYER] = LayerName.IXP
            data = [
                df
                for df in [df_borde, df_bras, df_caching, df_rai, df_ixp]
                if not df.empty
            ]
            df_interfaces = pd.concat(data, axis=0)
            if data:
                df_interfaces = pd.concat(data, axis=0)
                df_interfaces.drop_duplicates(inplace=True)
                df_interfaces.reset_index(drop=True, inplace=True)
                return df_interfaces
            else:
                return pd.DataFrame(columns=header_all_bbip)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todas las interfaces del BBIP para el día: {date} - {error}"
            )
            return pd.DataFrame(columns=header_all_bbip)

    def get_all_daily_summary_by_date(self, date: str | None = None) -> pd.DataFrame:
        """Get all daily layer summary data from the BBIP filtered by a specific date.

        :param date: Date to filter by. Format: YYYY-MM-DD.
        :type date: str
        :return DataFrame: Daily summary data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            if date and not Validate.date(date):
                raise Exception("The date is not valid.")
            df_borde = self.bbip_handler.get_all_daily_report(
                layer=LayerName.BORDE, date=date
            )
            df_bras = self.bbip_handler.get_all_daily_report(
                layer=LayerName.BRAS, date=date
            )
            df_caching = self.bbip_handler.get_all_daily_report(
                layer=LayerName.CACHING, date=date
            )
            df_rai = self.bbip_handler.get_all_daily_report(
                layer=LayerName.RAI, date=date
            )
            df_ixp = self.bbip_handler.get_all_daily_report(
                layer=LayerName.IXP, date=date
            )
            data: list[pd.DataFrame] = [
                df
                for df in [df_borde, df_bras, df_caching, df_rai, df_ixp]
                if not df.empty
            ]
            if data:
                df_daily_report = pd.concat(data, axis=0)
                df_daily_report.drop_duplicates(inplace=True)
                df_daily_report.reset_index(drop=True, inplace=True)
                return df_daily_report
            else:
                return pd.DataFrame(columns=header_daily)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todos los reportes diarios del BBIP del día: {date} - {error}"
            )
            return pd.DataFrame(columns=header_daily)

    def get_all_daily_data_on_week(self) -> pd.DataFrame:
        """Get all daily layer summary data from the BBIP for a week.

        :return DataFrame: Daily summary data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            df_daily_report = pd.DataFrame(columns=header_daily)
            date = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
            date_to = (
                datetime.now() - timedelta(days=datetime.now().weekday() + 1)
            ) + timedelta(days=1)
            while date.strftime("%Y-%m-%d") != date_to.strftime("%Y-%m-%d"):
                df = self.get_all_daily_summary_by_date(date=date.strftime("%Y-%m-%d"))
                if df_daily_report.empty and not df.empty:
                    df_daily_report = df
                elif not df.empty:
                    df_daily_report = pd.concat(
                        [df_daily_report, df], ignore_index=True
                    )
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
                date = date + timedelta(days=1)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todos los reportes diarios de la semana del BBIP - {error}"
            )
            return pd.DataFrame()
        else:
            return df_daily_report

    def get_all_daily_data_by_first_month(
        self, date_to: int | None = None
    ) -> pd.DataFrame:
        """Get all daily layer summary data from the BBIP from the first day of the month up to a specific date.

        :param date_to: End date for the range
        :type date_to: int, default today
        :return DataFrame: Daily summary data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            df_daily_report = pd.DataFrame(columns=header_daily)
            if not date_to:
                date_to_str = str(datetime.now().day)
            elif date_to and date_to < 10:
                date_to_str = f"0{date_to}"
            else:
                date_to_str = str(date_to)
            last_date = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d")[:-3] + "-" + date_to_str, "%Y-%m-%d"
            )
            first_date = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d")[:-3] + "-01", "%Y-%m-%d"
            )
            while first_date.strftime("%Y-%m-%d") != last_date.strftime("%Y-%m-%d"):
                df = self.get_all_daily_summary_by_date(
                    date=first_date.strftime("%Y-%m-%d")
                )
                if df_daily_report.empty and not df.empty:
                    df_daily_report = df
                elif not df.empty:
                    df_daily_report = pd.concat(
                        [df_daily_report, df], ignore_index=True
                    )
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
                first_date = first_date + timedelta(days=1)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todos los reportes diarios del BBIP del 01 hasta {date_to} - {error}"
            )
            return pd.DataFrame()
        else:
            return df_daily_report

    def get_all_daily_data_by_days_before(self, day_before: int = 30) -> pd.DataFrame:
        """Get all daily layer summary data from the BBIP from a specific number of days ago up to the current date.

        :param day_before: Number of days to look back from current date.
        :type day_before: int
        :return DataFrame: Daily summary data
        """
        try:
            if self.__error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            df_daily_report = pd.DataFrame(columns=header_daily)
            for day in range(day_before, 0, -1):
                date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
                df = self.get_all_daily_summary_by_date(date=date)
                if df_daily_report.empty and not df.empty:
                    df_daily_report = df
                elif not df.empty:
                    df_daily_report = pd.concat([df_daily_report, df], axis=0)
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
        except Exception as error:
            log.error(
                f"Layer handler. Fallo en la petición de todos los reportes diarios del BBIP {day_before} días antes - {error}"
            )
            return pd.DataFrame()
        else:
            return df_daily_report
