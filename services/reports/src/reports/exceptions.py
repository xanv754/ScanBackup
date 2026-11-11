class ProcessError(Exception):
    """A general error of the process: no layer is processed and the exit code is 2 [RF-044].

    It carries every cause found so that all of them are reported in a single run.
    """

    def __init__(self, causes: list[str]) -> None:
        """Keep the causes and build a message that lists them."""
        super().__init__("; ".join(causes))
        self.causes = causes


class InvalidInputError(ProcessError):
    """The command line parameters are invalid [RF-033]."""


class InvalidSettingsError(ProcessError):
    """The configuration file or the environment of the run is invalid [RF-032]."""


class DatabaseError(Exception):
    """MongoDB cannot be reached or an operation on it fails."""


class InvalidSheetNameError(Exception):
    """The canonical layer name cannot be used as a sheet name [RF-043]."""


class ExportError(Exception):
    """The report file cannot be written [RF-042]."""
