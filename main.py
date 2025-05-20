import click
from controllers.summary import SummaryController
from utils.validate import Validate


@click.group()
def cli():
    """CGPRD CLI.
    
    SystemCGPRD is a system to manage the data of the CGPRD.
    """
    pass


@cli.command(help="Get the day's summary report.")
@click.option("--date", required=False, help="Date to get data. Format YYYY-MM-DD")
def diary(date: str):
    """Get the day's summary report."""
    SummaryController.summary_diary_today()


if __name__ == "__main__":
    cli()