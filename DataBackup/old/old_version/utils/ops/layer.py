from scanbackup.constants import LayerName, DataPath, TableName


class LayerDetector:

    @staticmethod
    def get_folder_path(layer: str) -> str:
        """Gets the full folder path for a specific layer.

        :param layer: Layer to filter by.
        :type layer: str
        :return str: Folder path.
        """
        if layer == LayerName.BORDE:
            return DataPath.SCAN_DATA_BORDE
        elif layer == LayerName.BRAS:
            return DataPath.SCAN_DATA_BRAS
        elif layer == LayerName.CACHING:
            return DataPath.SCAN_DATA_CACHING
        elif layer == LayerName.RAI:
            return DataPath.SCAN_DATA_RAI
        elif layer == LayerName.IXP:
            return DataPath.SCAN_DATA_IXP
        elif layer == LayerName.IP_BRAS:
            return DataPath.SCAN_DATA_IP_BRAS
        elif layer == LayerName.DAILY_SUMMARY:
            return DataPath.SCAN_REPORT_DAILY
        else:
            raise FileNotFoundError(
                f"No se ha encontrado la especificación de la capa: {layer} en el sistema"
            )

    @staticmethod
    def get_table_name(layer: str) -> str:
        """Gets the database table name according to the layer.

        :param layer: Layer name.
        :type layer: str
        :return str: Layer table name.
        """
        if layer == LayerName.BORDE:
            return TableName.BORDE
        elif layer == LayerName.BRAS:
            return TableName.BRAS
        elif layer == LayerName.CACHING:
            return TableName.CACHING
        elif layer == LayerName.RAI:
            return TableName.RAI
        elif layer == LayerName.IXP:
            return TableName.IXP
        elif layer == LayerName.IP_BRAS:
            return TableName.IP_BRAS
        elif layer == LayerName.DAILY_SUMMARY:
            return TableName.DAILY_SUMMARY
        else:
            raise FileNotFoundError(
                f"No se ha encontrado la especificación de la capa: {layer} en el sistema"
            )
