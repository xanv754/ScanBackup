import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from bs4.element import Tag
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

    @staticmethod
    def safe_find(
        node: BeautifulSoup | Tag | None,
        layer: str,
        description: str,
        *args,
        **kwargs,
    ) -> Tag | None:
        """Busca una etiqueta HTML sin lanzar excepción; avisa por consola si no existe."""
        if node is None:
            return None
        result = node.find(*args, **kwargs)
        if result is None:
            print(
                f"{layer}: no se pudo encontrar '{description}' en la estructura HTML. "
                "Se omiten las fuentes de esta sección."
            )
        return result
