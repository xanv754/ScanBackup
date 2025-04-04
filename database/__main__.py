import click
from utils.log import LogHandler


@click.group()
def cli():
    """CPGRD Database

    CLI to controller database operations. Use with caution.
    """
    pass


@cli.command(help="Perfom database migrations.")
def migration():
    LogHandler.log("Starting migrations...", warn=True)
    #TODO: Execute migrations.
    LogHandler.log("Migrations completed", info=True)


@cli.command(help="Rollback database operations.")
def rollback():
    LogHandler.log("Starting rollback...", warn=True)
    #TODO: Execute rollbacks.
    LogHandler.log("Rollback completed", info=True)


if __name__ == "__main__":
    cli()
