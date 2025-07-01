from datetime import datetime


class Validate:
    """Class to validate parameters."""

    @staticmethod
    def month(month: str) -> bool:
        """Validate month to consult in database.

        Parameters
        ----------
        month : str
            Month to validate.
        """
        if (month.isdigit() and int(month) >= 1 and int(month) <= 12):
            return True
        else:
            return False
        
    @staticmethod
    def date(date: str) -> bool:
        """Validate date to consult in database.

        Parameters
        ----------
        date : str
            Date to validate.
        """
        try:
            validate = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            return validate == date
        except Exception:
            return False
