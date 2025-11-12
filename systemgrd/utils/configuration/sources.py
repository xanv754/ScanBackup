from systemgrd.utils.configuration.env import Environment


class URLBordeHuaweiEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_BORDE_HUAWEI")
            
            
class URLBordeCiscoEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_BORDE_CISCO")
    
    
class URLBordeJuniperEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_BORDE_JUNIPER")
    

class URLBrasHuaweiEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_BRAS_HUAWEI")
    
    
class URLCachingHuaweiEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_CACHING_HUAWEI")
    
    
class URLIxpEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_IXP")
    
    
class URLRaiHuaweiEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_RAI_HUAWEI")
    
    
class URLRaiZteEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_RAI_ZTE")
    
    
class URLIpBrasEnvironment(Environment):
    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_url(self) -> str | None:
        return self.get_env("SCAN_URL_IPBRAS")