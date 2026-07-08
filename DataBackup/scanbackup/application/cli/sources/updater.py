from pathlib import Path
from sources_scrapper.scrapper_scanbackup import UpdaterSources


def scrapper_sources(layer: str = "all", outdir: Path | None = None) -> None:
    updater = UpdaterSources()
    updater.execute(layer=layer, outpath=outdir)
