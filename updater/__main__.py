import click
from updater.handler.borde import BordeUpdaterHandler
from utils.log import LogHandler

@click.group
def cli():
    """CLI Updater Database"""
    pass

@cli.command(help="Upload data obtained to database")
def data():
    try:
        LogHandler.log("Starting updater border data...", warn=True)
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data()
        borderHandler.load_data(data=data)
    except Exception as e:
        LogHandler.log(f"Border data upload failed. {e}", err=True)
    finally:
        LogHandler.log("Updater border data finished", info=True)


if __name__ == "__main__":
    cli()
