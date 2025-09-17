import os
import requests
import pandas as pd
from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from systemgrd.constants import DataPath, HeaderSource, header_source
from systemgrd.model import Source
from systemgrd.utils import log, ConfigurationHandler


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # type: ignore


class SourceScrapping(ABC):
    config: ConfigurationHandler
    url_base: str
    with_capacity: str = "UNDEFINED"

    def __init__(self) -> None:
        self.config = ConfigurationHandler()

    def _compare_sources_old(self, new: pd.DataFrame, old: pd.DataFrame) -> pd.DataFrame:
        """Compare the new sources with the old ones.
        
        :param new: The new sources.
        :type new: pd.DataFrame
        :param old: The old sources.
        :type old: pd.DataFrame
        :returns DataFrame: Merge of new data and old data.
        """
        try:
            common = pd.merge(old, new, on=[HeaderSource.NAME, HeaderSource.MODEL], how="inner")
            common.drop(columns=[f'{HeaderSource.LINK}_x', f'{HeaderSource.CAPACITY}_y'], inplace=True)
            common.rename(columns={f'{HeaderSource.LINK}_y': HeaderSource.LINK, f'{HeaderSource.CAPACITY}_x': HeaderSource.CAPACITY}, inplace=True)
            common = common[[HeaderSource.LINK, HeaderSource.NAME, HeaderSource.CAPACITY, HeaderSource.MODEL]]
            news = pd.merge(new, old, on=[HeaderSource.NAME, HeaderSource.MODEL], how="left", indicator=True)
            news = news[news["_merge"] == "left_only"].drop("_merge", axis=1)
            news.drop(columns=[f'{HeaderSource.LINK}_y', f'{HeaderSource.CAPACITY}_y'], inplace=True)
            news.rename(columns={f'{HeaderSource.LINK}_x': HeaderSource.LINK, f'{HeaderSource.CAPACITY}_x': HeaderSource.CAPACITY}, inplace=True)
            news = news[[HeaderSource.LINK, HeaderSource.NAME, HeaderSource.CAPACITY, HeaderSource.MODEL]]
            if not common.empty and not news.empty:
                return pd.concat([common, news], ignore_index=True)
            elif not common.empty:
                return common
            else:
                return news
        except Exception as error:
            log.error(f"Failed to compare sources. {error}")
            return pd.DataFrame(columns=header_source)


    def set_url_base(self, url_complete: str) -> None:
        """Define the base path.
        
        :param url_complete: The complete url of the interface.
        :type url_complete: str
        """
        base = url_complete.split(".net")[0]
        self.url_base = base + ".net"

    def get_html(self, url: str) -> BeautifulSoup | None:
        """Get the HTML of the page.
        
        :returns BeutifulSoup | None: HTML information page.
        """
        try:
            html = requests.get(
                url, 
                verify=False, 
                auth=HTTPBasicAuth(self.config.scan_username, self.config.scan_password)
            )
            soup = BeautifulSoup(html.text, "html.parser")
        except Exception as error:
            log.error(f"Failed to obtain HTML from {url}. {error}")
            return None
        else:
            return soup
        
    def clear_name_format(self, name: str) -> str:
        """Clear the name format.
        
        :param name: The name to clear.
        :type name: str
        :return str: Link name formatted.
        """
        name = name.replace(" ", "_")
        name = name.replace("(", "")
        name = name.replace(")", "")
        name = name.replace("/", "")
        name = name.replace("%", "")
        name = name.replace("|", "-")
        return name

    def save_sources(self, sources: list[Source], layer: str) -> bool:
        """Save the sources in a file corresponding to their layer.
        
        :param sources: The list of sources to save.
        :type sources: list[Source]
        :param layer: The layer to save the sources.
        :type layer: str
        :return bool: Status of saved. True if saved successfully, otherwise False.
        """
        try:
            layer = layer.capitalize()
            df = self.transform_data_to_dataframe(sources)
            if df.empty: raise Exception("The data to save is empty.")
            source_path = os.path.join(DataPath.SCAN_SOURCES, f"{layer}.txt")
            old_source_path = os.path.join(DataPath.SCAN_SOURCES_BK, f"{layer}.txt")
            if os.path.exists(source_path):
                df_old = pd.read_csv(source_path, sep=" ", header=None, names=header_source) # type: ignore
                if not df_old.empty:
                    df_old[HeaderSource.MODEL] = df_old[HeaderSource.MODEL].astype(str)
                    df_old.sort_values(by=[HeaderSource.MODEL, HeaderSource.NAME], inplace=True)
                    df_old.to_csv(old_source_path, sep=" ", header=False, index=False)
                    data = self._compare_sources_old(df, df_old)
                    if data.empty: raise Exception("The data to save is empty.")
                else: data = df
            else: data = df
            data.sort_values(by=[HeaderSource.MODEL, HeaderSource.CAPACITY, HeaderSource.NAME], inplace=True)
            data.to_csv(source_path, sep=" ", header=False, index=False)
        except Exception as error:
            log.error(f"Failed to save sources: {layer}. {error}")
            return False
        else:
            return True
        
    def transform_data_to_dataframe(self, data: list[Source]) -> pd.DataFrame:
        """Transform the data to a dataframe.
        
        :param data: The data to transform.
        :type data: list[Source]
        :returns DataFrame: DataFrame of model data.
        """
        try:
            json = [interface.model_dump() for interface in data]
            df = pd.DataFrame(json)
            return df
        except Exception as error:
            log.error(f"Failed to transform data to dataframe. {error}")
            return pd.DataFrame(columns=header_source)
        
    @abstractmethod  
    def get_capacity(self, param: str) -> str:
        """Get the capacity of an interface.
        
        :param param: The name or url of the interface.
        :type param: str
        :return str: Capacity of link.
        """
        pass

    @abstractmethod  
    def get_sources(self) -> list[Source]:
        """Get a list of sources for each existing interface.
        
        :returns List[Source]: SCAN's link of a layer.
        """
        pass