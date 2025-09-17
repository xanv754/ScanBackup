import os
from dotenv import load_dotenv, dotenv_values
from systemgrd.utils.log import log


load_dotenv(override=True)


class ConfigurationHandler:
    """Handler to get all configuration to system."""

    uri_postgres: str
    uri_mongo: str
    scan_username: str
    scan_password: str
    scan_url_borde_huawei: str
    scan_url_borde_cisco: str
    scan_url_bras: str
    scan_url_caching: str
    scan_url_rai_hw: str
    scan_url_rai_zte: str
    scan_url_ixp: str

    def __init__(self, dev: bool = False, test: bool = False) -> None:
        try:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            if dev and os.path.exists(f"{base_path}/.env.development"):
                env = dotenv_values(f"{base_path}/.env.development")
            elif test and os.path.exists(f"{base_path}/.env.testing"):
                env = dotenv_values(f"{base_path}/.env.testing")
            elif not dev and not test and os.path.exists(f"{base_path}/.env.production"):
                env = dotenv_values(f"{base_path}/.env.production")
            elif not dev and not test and os.path.exists(f"{base_path}/.env"):
                env = dotenv_values(f"{base_path}/.env")
            else: raise FileNotFoundError("No file with environment variables found")
            uri_mongo = env.get("URI_MONGO")
            if uri_mongo: self.uri_mongo = uri_mongo
            else:
                log.warning(f"Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
            scan_username = env.get("SCAN_USERNAME")
            if scan_username: self.scan_username = scan_username
            else:
                log.warning(f"Failed to obtain configuration. SCAN_USERNAME variable not found in enviroment file")
            scan_password = env.get("SCAN_PASSWORD")
            if scan_password: self.scan_password = scan_password
            else:
                log.warning(f"Failed to obtain configuration. SCAN_PASSWORD variable not found in enviroment file")
            scan_url_borde_hw = env.get("SCAN_URL_BORDE_HW")
            if scan_url_borde_hw: self.scan_url_borde_huawei = scan_url_borde_hw
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_BORDE variable not found in enviroment file")
            scan_url_borde_cisco = env.get("SCAN_URL_BORDE_CISCO")
            if scan_url_borde_cisco: self.scan_url_borde_cisco = scan_url_borde_cisco
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_BORDE_CISCO variable not found in enviroment file")
            scan_url_bras = env.get("SCAN_URL_BRAS")
            if scan_url_bras: self.scan_url_bras = scan_url_bras
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_BRAS variable not found in enviroment file")
            scan_url_caching = env.get("SCAN_URL_CACHING")
            if scan_url_caching: self.scan_url_caching = scan_url_caching
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_CACHING variable not found in enviroment file")
            scan_url_rai_hw = env.get("SCAN_URL_RAI_HW")
            if scan_url_rai_hw: self.scan_url_rai_hw = scan_url_rai_hw
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_RAI_HW variable not found in enviroment file")
            scan_url_rai_zte = env.get("SCAN_URL_RAI_ZTE")
            if scan_url_rai_zte: self.scan_url_rai_zte = scan_url_rai_zte
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_RAI_ZTE variable not found in enviroment file")
            scan_url_ixp = env.get("SCAN_URL_IXP")
            if scan_url_ixp: self.scan_url_ixp = scan_url_ixp
            else:
                log.warning(f"Failed to obtain configuration. SCAN_URL_IXP variable not found in enviroment file")
        except Exception as error:
            log.error(f"Failed to obtain configuration. {error}")
            exit(1)


if __name__ == "__main__":
    config = ConfigurationHandler(dev=True)
    print(config.uri_mongo)
