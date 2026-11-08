class ProcessError(Exception):
    """A general error of the process: nothing is collected and the exit code is 2 [RF-028].

    It carries every cause found so that all of them are reported in a single run.
    """

    def __init__(self, causes: list[str]) -> None:
        """Keep the causes and build a message that lists them."""
        super().__init__("; ".join(causes))
        self.causes = causes


class InvalidSettingsError(ProcessError):
    """The configuration or the environment of the run is invalid."""


class DatabaseError(Exception):
    """MongoDB cannot be reached or an operation on it fails."""
