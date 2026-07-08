from scanbackup.shared import Configuration


class ValidatorConfig:
    @staticmethod
    def valid_layer_bbip(name: str) -> bool:
        name = name.upper()
        config = Configuration()
        cfg_layers = config.get_cfg_layers()
        layers = [layer.upper() for layer in cfg_layers.bbip.names]
        return name in layers

    @staticmethod
    def valid_layer_ip(name: str) -> bool:
        name = name.upper()
        config = Configuration()
        cfg_layers = config.get_cfg_layers()
        layers = [layer.upper() for layer in cfg_layers.ip.names]
        return name in layers
