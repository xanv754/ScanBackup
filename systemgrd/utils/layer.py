from systemgrd.constants import LayerName, DataPath, TableName


class LayerDetector:
    
    @staticmethod
    def get_folder_path(layer: str) -> str:
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
        elif layer == LayerName.DAILY_REPORT:
            return DataPath.SCAN_REPORT_DAILY
        else:
            raise FileNotFoundError(f"Not found data of the layer: {layer}")
        
    @staticmethod
    def get_table_name(layer: str) -> str:
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
        elif layer == LayerName.DAILY_REPORT:
            return TableName.DAILY_REPORT
        else:
            raise FileNotFoundError(f"Not found data of the layer: {layer}")