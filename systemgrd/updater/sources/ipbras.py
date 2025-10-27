import os
from systemgrd.model import Source
from systemgrd.updater.sources.scrapping import SourceScrapping
from systemgrd.utils import log


class IPBrasSourceScrapping(SourceScrapping):

    def get_capacity(self, param: str) -> str:
        """Dummy implementation for abstract method, not used for IPBras."""
        return self.with_capacity

    def get_sources(self) -> list[Source]:
        """Obtain sources from IPBras.txt file since IPBras uses predefined URLs."""
        try:
            sources = []
            ipbras_file = os.path.join("sources", "SCAN", "IPBras.txt")
            if os.path.exists(ipbras_file):
                with open(ipbras_file, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            link = parts[0]
                            name = parts[1]
                            capacity = parts[2]
                            model = parts[3]
                            source = Source(
                                link=link,
                                name=name,
                                capacity=capacity,
                                model=model,
                            )
                            sources.append(source)
            return sources
        except Exception as error:
            log.error(f"Failed to obtain sources from IPBras.txt. {error}")
            return []
