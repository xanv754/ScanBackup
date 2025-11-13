import os
import requests
import pandas as pd
from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from scanbackup.constants import DataPath, HeaderSource, header_source
from scanbackup.model import Source
from scanbackup.utils import log, UserEnvironment
from scanbackup.updater.utils.transform import TransForm


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Scrapping(ABC):
    _add_sources: bool
    _url: str
    _layer: str
    _separator: str = ";"
    _dev: bool
    
    def __init__(self, url: str, layer: str, add: bool = False, dev: bool = False):
        self._url = url
        self._layer = layer
        self._add_sources = add
        self._dev = dev
        
    def _compare_sources_old(self, new_data: pd.DataFrame, old_data: pd.DataFrame) -> pd.DataFrame:
        """Compare the new sources with the old ones.
        
        :returns DataFrame: Merge of new data and old data.
        """
        try:
            model_filter = new_data[HeaderSource.MODEL].iloc[0]
            preserved_data = old_data[old_data[HeaderSource.MODEL] != model_filter]
            old_data_to_compare = old_data[old_data[HeaderSource.MODEL] == model_filter]
            if not old_data_to_compare.empty:    
                merge_data = pd.merge(
                    old_data_to_compare, new_data, 
                    on=[HeaderSource.NAME, HeaderSource.MODEL], 
                    how="inner"
                )
                merge_data.drop(
                    columns=[f"{HeaderSource.LINK}_x", f"{HeaderSource.CAPACITY}_y"],
                    inplace=True,
                )
                merge_data.rename(
                    columns={
                        f"{HeaderSource.LINK}_y": HeaderSource.LINK,
                        f"{HeaderSource.CAPACITY}_x": HeaderSource.CAPACITY,
                    },
                    inplace=True,
                )
                merge_data = merge_data[[
                    HeaderSource.LINK, HeaderSource.NAME, 
                    HeaderSource.CAPACITY, HeaderSource.MODEL
                ]]
            else: merge_data = new_data
            all_data = pd.concat([preserved_data, merge_data], axis=0)
            all_data.sort_values(
                [HeaderSource.MODEL, HeaderSource.CAPACITY, HeaderSource.NAME], 
                inplace=True
            )
            return all_data
        except Exception as error:
            log.error(f"Fallo al comparar las fuentes existentes con las obtenidas recientemente - {error}")
            return pd.DataFrame(columns=header_source)
        
    def _create_backup(self, df: pd.DataFrame) -> None:
        """Create backup of existing sources."""
        os.makedirs(DataPath.SCAN_SOURCES_BK, exist_ok=True)
        bk_source_path = os.path.join(DataPath.SCAN_SOURCES_BK, self._layer)
        df[HeaderSource.MODEL] = df[HeaderSource.MODEL].astype(str)
        df.sort_values(by=[HeaderSource.MODEL, HeaderSource.NAME], inplace=True)
        df.to_csv(bk_source_path, sep=self._separator, header=False, index=False)
    
    def get_html(self, url: str) -> BeautifulSoup | None:
        """Get the HTML of the page.

        :param url: URL of the page.
        :type url: str
        :returns BeutifulSoup: HTML information page. Otherwise return `None`.
        """
        try:
            if self._dev: env = UserEnvironment(dev=True)
            else: env = UserEnvironment()
            username = env.get_username()
            password = env.get_password()
            html = requests.get(
                url,
                verify=False,
                auth=HTTPBasicAuth(username, password)
            )
            soup = BeautifulSoup(html.text, "html.parser")
            if not soup: raise Exception("No se obtuvo información del HTML")
        except Exception as error:
            log.error(f"Fallo al obtener la estructura HTML de la página: {self._url}, capa: {self._layer} - {error}")
            return None
        else:
            return soup
        
    @abstractmethod
    def get_sources(self, html: BeautifulSoup) -> list[Source]:
        """Get information about sources by scraping the page."""
        pass
    
    @abstractmethod
    def get_capacity(self) -> list[Source]:
        """Get information about capacity of a link by scraping the page."""
        pass
    
    def get_url(self) -> str:
        """Get the URL for scraping."""
        return self._url
    
    def save_sources(self, sources: list[Source]) -> bool:
        """Save the sources in a file corresponding to their layer.

        :param sources: The list of sources to save.
        :type sources: list[Source]
        :param layer: The layer to save the sources.
        :type layer: str
        :return bool: Status of saved. True if saved successfully, otherwise False.
        """
        try:
            new_sources = TransForm.model_to_df(models=sources)
            os.makedirs(DataPath.SCAN_SOURCES, exist_ok=True)
            source_path = os.path.join(DataPath.SCAN_SOURCES, self._layer)
            if os.path.exists(source_path):
                existing_sources = pd.read_csv(source_path, sep=self._separator, header=None, names=header_source)
                if not self._add_sources: self._create_backup(existing_sources)
                new_sources = self._compare_sources_old(new_data=new_sources, old_data=existing_sources)
                if new_sources.empty: raise Exception("La comparación de fuentes falló")
            new_sources.sort_values(
                [HeaderSource.MODEL, HeaderSource.CAPACITY, HeaderSource.NAME], 
                inplace=True
            )
            new_sources.to_csv(source_path, sep=self._separator, header=False, index=False)
        except Exception as error:
            log.error(f"Fallo al guardar las fuentes nuevas de la capa {self._layer} - {error}")
            return False
        else:
            return True
        
    def run(self) -> bool:
        """Execute the updater of layer."""
        try:
            page = self.get_html(self.get_url())
            if not page: raise Exception()
            sources = self.get_sources(html=page)
            if not sources: raise Exception(f"No se obtuvo ninguna de la fuentes de la capa {self._layer}")
            return self.save_sources(sources)
        except Exception as error:
            log.error(f"Falló al realizar la actualización de fuentes de la capa {self._layer} - {error}")
            return False