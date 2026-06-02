import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from scrapper_scanbackup.utils.config.model import CredentialModel
from scrapper_scanbackup.utils.config.load import ScrapperSetting
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Scrapper:
    @staticmethod
    def get_html(
        url: str, credentials: CredentialModel | None = None
    ) -> BeautifulSoup | None:
        if not credentials:
            setting = ScrapperSetting()
            credentials = setting.get_scan_credentials()
        html = requests.get(
            url,
            verify=False,
            auth=HTTPBasicAuth(credentials.username, credentials.password),
        )
        soup = BeautifulSoup(html.text, "html.parser")
        return soup
