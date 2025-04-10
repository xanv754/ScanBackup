import click
from updater.handler.borde import BordeUpdaterHandler
from utils.log import LogHandler

@click.group
def cli():
    """CLI Updater Database"""
    pass

@cli.command(help="Upload data obtained to database")
@click.option("--date", required=False, help="Date to upload data. Format YYYY-MM-DD")
def data(date: str):
    try:
        LogHandler.log("Starting updater borde data...", warn=True)
        borderHandler = BordeUpdaterHandler()
        if date:
            data_borde = borderHandler.get_data(date=date)
        else:
            data_borde = borderHandler.get_data()
        borderHandler.load_data(data=data_borde)
    except Exception as e:
        LogHandler.log(f"Borde data upload failed. {e}", err=True)
    finally:
        LogHandler.log("Updater borde data finished", info=True)


if __name__ == "__main__":
    cli()
