class InvalidConfigError(Exception):
    """Raised when `config.yml` is invalid. Holds every cause that was detected."""

    def __init__(self, causes: list[str]) -> None:
        """Store the causes and build a summary message from them."""
        self.causes = causes
        super().__init__("; ".join(causes))
