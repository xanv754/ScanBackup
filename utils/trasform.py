from typing import List
from model.boder import BorderModel
from storage.constant.fields import BordeFieldDatabase


class BordeResponseTrasform:
    @staticmethod
    def trasformBorderModel(data: List[dict]) -> List[BorderModel]:
        """Transform response of database to model.
        
        Parameters
        ----------
        data : List[dict]
            Data borde interfaces.
        """
        data_transform: List[BorderModel] = []
        for interface in data:
            data_transform.append(
                BorderModel(
                    interface=interface[BordeFieldDatabase.INTERFACE],
                    model=interface[BordeFieldDatabase.MODEL],
                    capacity=interface[BordeFieldDatabase.CAPACITY]
                )
            )
        return data_transform