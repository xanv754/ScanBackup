from constants.group import LayerType

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

