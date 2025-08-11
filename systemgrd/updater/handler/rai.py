import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from systemgrd.constants import DataPath, HeaderBBIP, header_bbip, header_upload_scan_data
from systemgrd.database import RaiMongoQuery
from systemgrd.model import BBIPModel, Source
from systemgrd.updater.update import UpdaterHandler
from systemgrd.updater.scrapping import SourceScrapping
from systemgrd.utils import log


class RaiUpdaterHandler(UpdaterHandler):
    """Rai data updater handler."""

    def get_data(self, folderpath: str | None = None, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            if not folderpath: folderpath = DataPath.SCAN_DATA_RAI
            if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
                raise FileNotFoundError("Rai folder not found.")
            if not date: date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            files = [filename for filename in os.listdir(folderpath)]
            df_to_upload = pd.DataFrame(columns=header_bbip)
            for filename in files:
                try:
                    type = filename.split("%")[0]
                    interface = filename.split("%")[1]
                    capacity = filename.split("%")[2]
                    df_data = pd.read_csv(f"{folderpath}/{filename}", sep=" ", header=None, names=header_upload_scan_data)
                    if not force: df_data = df_data[df_data[HeaderBBIP.DATE] == date]
                    if not df_data.empty:
                        df_data[HeaderBBIP.NAME] = interface
                        df_data[HeaderBBIP.CAPACITY] = capacity
                        df_data[HeaderBBIP.TYPE] = type
                        if df_to_upload.empty: df_to_upload = df_data
                        else: df_to_upload = pd.concat([df_to_upload, df_data], axis=0)
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue                    
        except Exception as e:
            log.error(f"Failed to data load of Rai layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_to_upload

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty: 
                log.warning("The system received empty data Rai when it updated.")
                return False
            query = RaiMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [BBIPModel(**item) for item in data_json]
            except Exception as e:
                log.error(f"Failed to validate data with the model. Rai updater system has suspended. {e}")
                return False
            else:
                response = query.new_interface(json)
                return response
        except Exception as e:
            log.error(f"Failed to load data of Rai layer. {e}")
            return False


class RaiSourceScrapping(SourceScrapping):

    def _get_info_interfaces(self, soup: BeautifulSoup) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            model = "DEDICADO"
            blocks = soup.find('section', {'id': 'features'}).find('div', class_="container").find('div', class_="row").find_all('div', class_="col-sm-12")
            for item in blocks:
                link_original = item.find('li', {'id': 'graficas'}).find('a').get('href')
                link = link_original.replace(".html", ".log")
                name = item.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                name = name.split(" ")
                del name[0]
                name = " ".join(name)
                name = name.split(" - ")[0]
                name = name.replace("/", "").replace("(", "").replace(")", "").replace("%", "").replace("|", "-").replace(" ", "_")
                capacity = self.get_capacity(link_original)
                source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=model)
                sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Rai interfaces. {error}")
            return []
        else:
            return sources
        
    def _scrap_rai_hw(self) -> list[Source]:
        """Scrapping the information to obtain the sources Rai Huawei."""
        self.set_url_base(self.config.scan_url_rai_hw)
        soup = self.get_html(self.config.scan_url_rai_hw)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Rai Huawei.")
            return []
        return self._get_info_interfaces(soup)

    def _scrap_rai_zte(self) -> list[Source]:
        """Scrapping the information to obtain the sources Rai ZTE."""
        self.set_url_base(self.config.scan_url_rai_zte)
        soup = self.get_html(self.config.scan_url_rai_zte)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Rai ZTE.")
            return []
        return self._get_info_interfaces(soup)

    def get_capacity(self, param: str): 
        # TODO
        return self.with_capacity

    def get_sources(self):
        try:
            sources_hw = self._scrap_rai_hw()
            sources_zte = self._scrap_rai_zte()
            return sources_hw + sources_zte
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Rai interfaces. {error}")
            return []