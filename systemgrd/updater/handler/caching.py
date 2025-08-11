import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from systemgrd.constants import DataPath, HeaderBBIP, header_bbip, header_upload_scan_data
from systemgrd.database import CachingMongoQuery
from systemgrd.model import BBIPModel, Source
from systemgrd.updater.update import UpdaterHandler
from systemgrd.updater.scrapping import SourceScrapping
from systemgrd.utils import log


class CachingUpdaterHandler(UpdaterHandler):
    """Caching data updater handler."""

    def get_data(self, folderpath: str | None = None, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            if not folderpath: folderpath = DataPath.SCAN_DATA_CACHING
            if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
                raise FileNotFoundError("Caching folder not found.")
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
            log.error(f"Failed to data load of Caching layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_to_upload

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty: 
                log.warning("The system received empty data Caching when it updated.")
                return False
            query = CachingMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [BBIPModel(**item) for item in data_json]
            except Exception as e:
                log.error(f"Failed to validate data with the model. Caching updater system has suspended. {e}")
                return False
            else:
                response = query.new_interface(json)
                return response
        except Exception as e:
            log.error(f"Failed to load data of Caching layer. {e}")
            return False


class CachingSourceScrapping(SourceScrapping):

    def _conditional_special_case(self, service: str) -> str:
        """Special case for some services."""
        if "ALIANZA" in service: return "FACEBOOK"
        else: return service

    def _get_list_services(self, soup: BeautifulSoup) -> list[str, str]:
        """Scrapping the information to obtain a list of bras existing."""
        services = []
        blocks = soup.find('div', class_="sidebar").find('nav', class_="mt-2").find('ul', class_="nav nav-pills nav-sidebar flex-column").find('li', class_="nav-item menu-open").find('ul', class_="nav nav-treeview").find_all('li', class_="nav-item")
        del blocks[0]
        for item in blocks:
            block = item.find('a', class_="nav-link")
            link = block.get('href')
            if link == "#": continue
            service = block.find('p').get_text(strip=True)
            service = service.replace("Suma", "").strip().upper()
            service = self._conditional_special_case(service)
            services.append((service, link))
        return services

    def _get_info_interfaces(self) -> list[Source]:
        """Scrapping the information to obtain the sources for each interface."""
        try:
            sources = []
            junk_interface = "Sumatoria"
            soup = self.get_html(self.config.scan_url_caching)
            if not soup: 
                log.error("Failed to obtain sources from SCAN Caching.")
                return []
            services = self._get_list_services(soup)
            for service in services:
                soup = self.get_html(f"{self.url_base}{service[1]}")
                if not soup: 
                    log.error(f"Failed to obtain info from SCAN Caching {service[0]}.")
                    continue
                blocks = soup.find('section', class_="content").find('div', class_="row").find('div', class_="col-md-12").find_all('div', class_="col-sm-12")
                for item in blocks:
                    name = item.find('li', {'id': 'subtitulo'}).get_text(strip=True)
                    if not name or junk_interface in name: continue
                    name = name.split(" - ")[0].replace("Router ", "").replace(" ", "_").replace("/", "").replace("(", "").replace(")", "").replace("%", "").replace("|", "-")
                    capacity = self.get_capacity(name)
                    link_original = item.find('li', {'id': 'graficas'}).find('a').get('href')
                    link = link_original.replace(".html", ".log")
                    source = Source(link=f"{self.url_base}{link}", name=name, capacity=capacity, model=service[0])
                    sources.append(source)
        except Exception as error:
            log.error(f"Failed to obtain info from SCAN Caching interfaces. {error}")
            return []
        else:
            return sources

    def get_capacity(self, param: str): 
        # TODO
        return self.with_capacity

    def get_sources(self):
        self.set_url_base(self.config.scan_url_caching)
        return self._get_info_interfaces()
