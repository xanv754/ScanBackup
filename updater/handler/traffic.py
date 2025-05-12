from typing import List
from datetime import datetime
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
# from database.querys.traffic.postgres import PostgresTrafficHistoryQuery
from utils.log import log


class TrafficHistoryUpdaterHandler(UpdaterHandler):
    """Class to get history data of files."""

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[TrafficHistoryModel]:
        try:
            if filepath:
                traffic: List[TrafficHistoryModel] = []
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d")
                with open(filepath, "r") as file:
                    lines = file.readlines()
                    for line in lines[1:]:
                        date_data = line.split(" ")[0]
                        if date == date_data:
                            new_traffic = TrafficHistoryModel(
                                date=line.split(" ")[0],
                                time=line.split(" ")[1],
                                idLayer="",
                                typeLayer="",
                                inProm=int(line.split(" ")[2]),
                                outProm=int(line.split(" ")[3]),
                                inMax=int(line.split(" ")[4]),
                                outMax=int(line.split(" ")[5]),
                            )
                            traffic.append(new_traffic)
                return traffic
            return []
        except Exception as e:
            log.error(f"Failed to get data of history traffic. {e}")
            return []

    def load_data(self, data: List[TrafficHistoryModel], mongo: bool = False, postgres: bool = False) -> bool:
        failed = False
        if mongo and len(data) > 0:
            try:
                mongo_database = MongoTrafficHistoryQuery()
                response = mongo_database.new_traffic(traffic=data)
                if not response:
                    raise Exception(f"Failed to insert histories traffic of {data[0].typeLayer} into mongo database.")
            except Exception as e:
                log.error(f"Failed to load data of history traffic. {e}")
                failed = True
        # if postgres and len(data) > 0:
        #     try:
        #         postgres_database = PostgresTrafficHistoryQuery()
        #         response = postgres_database.new_traffic(traffic=data)
        #         if not response:
        #             raise Exception(f"Failed to insert histories traffic of {data[0].typeLayer} into postgres database.")
        #     except Exception as e:
        #         log.error(f"Failed to load data of history traffic. {e}")
        #         failed = True
        return not failed
