import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from systemgrd.constants import DataPath, HeaderBBIP, header_bbip, header_upload_scan_data
from systemgrd.database import BrasMongoQuery
from systemgrd.model import BBIPModel, Source
from systemgrd.updater.update import UpdaterHandler
from systemgrd.updater.scrapping import SourceScrapping
from systemgrd.utils import log


class BrasUpdaterHandler(UpdaterHandler):
    """Bras data updater handler."""
            
    def get_data(self, folderpath: str | None = None, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            if not folderpath: folderpath = DataPath.SCAN_DATA_BRAS
            if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
                raise FileNotFoundError("Bras folder not found.")
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
            log.error(f"Failed to data load of Bras layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_to_upload

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty: 
                log.warning("The system received empty data Bras when it updated.")
                return False
            query = BrasMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [BBIPModel(**item) for item in data_json]
            except Exception as e:
                log.error(f"Failed to validate data with the model. Bras updater system has suspended. {e}")
                return False
            else:
                response = query.new_interface(json)
                return response
        except Exception as e:
            log.error(f"Failed to load data of Bras layer. {e}")
            return False
        
        
class BrasSourceScrapping(SourceScrapping):

    def _get_list_bras(self, soup: BeautifulSoup, uplink: bool) -> list[str, str]:
        """Scrapping the information to obtain a list of bras existing."""
        elements = []
        if uplink: content = "UPLINK POR BRAS"
        else: content = "DOWNLINK POR BRAS"
        menu = soup.find('div', class_="sidebar").find('nav').find('ul', class_='nav nav-pills nav-sidebar flex-column').find_all('li', class_="nav-item menu")
        for level in menu:
            block = level.find("ul", class_="nav nav-treeview").find_all('li', class_="nav-item")
            for item in block:
                if item.find('p').get_text(strip=True) == content:
                    all_bras = item.find('ul', class_="nav nav-treeview").find_all('li', class_="nav-item")
                    for bras in all_bras:
                        link = bras.find('a').get('href')
                        name = bras.find('p').get_text(strip=True)
                        elements.append((name, link))
        return elements

    def _get_info_interfaces(self, soup: BeautifulSoup, uplink: bool) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            list_bras = self._get_list_bras(soup, uplink=uplink)
            for bras in list_bras:
                soup = self.get_html(self.url_base + bras[1])
                if not soup: 
                    log.error(f"Failed to obtain info from SCAN Bras {bras[0]}.")
                    continue
                blocks = soup.find('section', class_="content").find_all('div', class_="col-sm-12")
                del blocks[0]
                for block in blocks:
                    name = block.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                    preffix = name.split(" - ")[0].strip()
                    preffix = self.clear_name_format(preffix)
                    suffix = name.split(" - ")[1].strip()
                    suffix = self.clear_name_format(suffix)
                    name = preffix + "_-_" + suffix
                    link_original = block.find('li', {'id': 'graficas'}).find('a').get('href')
                    link = link_original.replace(".html", ".log")
                    capacity = self.get_capacity(name)
                    if uplink: model = "UPLINK"
                    else: model = "DOWNLINK"
                    source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=model)
                    sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Bras interfaces. {error}")
            return []
        else:
            return sources
        
    def get_capacity(self, param: str):
        try:
            name_split = param.split("_")
            for content in name_split:
                content = content.upper().strip()
                if "GB" in content:
                    content = content.replace("GB", "")
                    return content
            return "5"
        except Exception as error:
            log.error(f"Failed to obtain capacity from {param}. {error}")
            return self.with_capacity

    def get_sources(self):
        self.set_url_base(self.config.scan_url_bras)
        soup = self.get_html(url=self.config.scan_url_bras)
        if not soup: 
            log.error("Failed to obtain sources from SCAN Bras.")
            return []
        sources_uplink = self._get_info_interfaces(soup, uplink=True)
        sources_downlink = self._get_info_interfaces(soup, uplink=False)
        return sources_uplink + sources_downlink