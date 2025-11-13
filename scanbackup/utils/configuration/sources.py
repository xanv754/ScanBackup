from scanbackup.utils.configuration.env import Environment


class URLBordeHuaweiEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the Borde Huawei URL."""
        return self.get_env("SCAN_URL_BORDE_HUAWEI")
            
            
class URLBordeCiscoEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the Borde Cisco URL."""
        return self.get_env("SCAN_URL_BORDE_CISCO")
    
    
class URLBordeJuniperEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the Borde Juniper URL."""
        return self.get_env("SCAN_URL_BORDE_JUNIPER")
    

class URLBrasHuaweiEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the Bras Huawei URL."""
        return self.get_env("SCAN_URL_BRAS_HUAWEI")
    
    
class URLCachingHuaweiEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the Caching Huawei URL."""
        return self.get_env("SCAN_URL_CACHING_HUAWEI")
    
    
class URLIxpEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the IXP URL."""
        return self.get_env("SCAN_URL_IXP")
    
    
class URLRaiHuaweiEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the RAI Huawei URL."""
        return self.get_env("SCAN_URL_RAI_HUAWEI")
    
    
class URLRaiZteEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the RAI ZTE URL."""
        return self.get_env("SCAN_URL_RAI_ZTE")
    
    
class URLIpBrasEnvironment(Environment):
    def __init__(
        self, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(dev, testing)

    def get_url(self) -> str | None:
        """Gets the IP Bras URL."""
        return self.get_env("SCAN_URL_IPBRAS")