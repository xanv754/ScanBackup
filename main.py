import click
from controllers.summary import SummaryController


@click.group()
def cli():
    """CGPRD CLI.
    
    SystemCGPRD is a system to manage the data of the CGPRD.
    """
    pass


@cli.command(help="Get a summary report of the current day's data.")
@click.option("--date", required=False, help="Date to get data. Format YYYY-MM-DD")
def diary(date: str):
    SummaryController.summary_diary_current()

@cli.command(help="Get a summary of the current fortnight's data.")
def fortnight():
    SummaryController.summary_fortnight_current()

@cli.command(help="Get a summary of the current weekly's data.")
def weekly():
    SummaryController.summary_weekly_current()

@cli.command(help="Obtain a summary of the current month's data.")
def monthly():
    SummaryController.summary_monthly_current()


if __name__ == "__main__":
    cli()