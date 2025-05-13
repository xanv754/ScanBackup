from constants import LayerType


class Validate:
    """Class to validate parameters."""

    @staticmethod
    def layer_type(layer: str) -> bool:
        """Validate layer type to consult in database.

        Parameters
        ----------
        layer : str
            Layer type to validate.
        """
        if ((layer == LayerType.BORDE) or 
            (layer == LayerType.BRAS) or 
            (layer == LayerType.CACHING) or 
            (layer == LayerType.RAI) or 
            (layer == LayerType.IP_HISTORY)
        ):
            return True
        else:
            return False

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
        if "-" in date:
            content = date.split("-")
            if len(content) == 3:
                if content[0].isdigit() and content[1].isdigit() and content[2].isdigit():
                    return True
        return False
