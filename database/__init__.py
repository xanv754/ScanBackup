from database.constant.tables import TableNameDatabase
from database.constant.fields import (
    BordeFieldDatabase,
    BrasFieldDatabase,
    CachingFieldDatabase,
    RaiFieldDatabase,
    TrafficHistoryFieldDatabase,
    IPHistoryFieldDatabase, 
    DailyReportFieldDatabase
)
from database.schemas.mongo.borde import BORDE_SCHEMA as BORDE_SCHEMA_MONGO
from database.schemas.mongo.bras import BRAS_SCHEMA as BRAS_SCHEMA_MONGO
from database.schemas.mongo.caching import CACHING_SCHEMA as CACHING_SCHEMA_MONGO
from database.schemas.mongo.rai import RAI_SCHEMA as RAI_SCHEMA_MONGO
from database.schemas.mongo.trafficHistory import TRAFFIC_HISTORY_SCHEMA as TRAFFIC_HISTORY_SCHEMA_MONGO
from database.schemas.mongo.ipHistory import IP_HISTORY_SCHEMA as IP_HISTORY_SCHEMA_MONGO
from database.schemas.mongo.dailyReport import DAILY_REPORT_SCHEMA as DAILY_REPORT_SCHEMA_MONGO
from database.schemas.postgres.borde import BORDE_SECUENCE_SCHEMA as BORDE_SECUENCE_SCHEMA_POSTGRES
from database.schemas.postgres.borde import BORDE_SCHEMA as BORDE_SCHEMA_POSTGRES
from database.schemas.postgres.bras import BRAS_SECUENCE_SCHEMA as BRAS_SECUENCE_SCHEMA_POSTGRES
from database.schemas.postgres.bras import BRAS_SCHEMA as BRAS_SCHEMA_POSTGRES
from database.schemas.postgres.caching import CACHING_SECUENCE_SCHEMA as CACHING_SECUENCE_SCHEMA_POSTGRES
from database.schemas.postgres.caching import CACHING_SCHEMA as CACHING_SCHEMA_POSTGRES
from database.schemas.postgres.rai import RAI_SECUENCE_SCHEMA as RAI_SECUENCE_SCHEMA_POSTGRES
from database.schemas.postgres.rai import RAI_SCHEMA as RAI_SCHEMA_POSTGRES
from database.schemas.postgres.trafficHistory import TRAFFIC_HISTORY_SCHEMA as TRAFFIC_HISTORY_SCHEMA_POSTGRES
from database.schemas.postgres.ipHistory import IP_HISTORY_SCHEMA as IP_HISTORY_SCHEMA_POSTGRES
from database.schemas.postgres.dailyReport import DAILY_REPORT_SCHEMA as DAILY_REPORT_SCHEMA_POSTGRES
from database.libs.product.database import Database
from database.libs.product.mongo import MongoDatabase
from database.libs.product.postgres import PostgresDatabase
from database.libs.factory.database import DatabaseFactory
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.factory.postgres import PostgresDatabaseFactory
from database.querys.borde.borde import BordeQuery
from database.querys.borde.mongo import MongoBordeQuery
from database.querys.borde.postgres import PostgresBordeQuery
from database.querys.bras.bras import BrasQuery
from database.querys.bras.mongo import MongoBrasQuery
from database.querys.bras.postgres import PostgresBrasQuery
from database.querys.caching.caching import CachingQuery
from database.querys.caching.mongo import MongoCachingQuery
from database.querys.caching.postgres import PostgresCachingQuery
from database.querys.rai.rai import RaiQuery
from database.querys.rai.mongo import MongoRaiQuery
from database.querys.rai.postgres import PostgresRaiQuery
from database.querys.traffic.traffic import TrafficHistoryQuery
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
from database.querys.traffic.postgres import PostgresTrafficHistoryQuery
from database.querys.reports.daily.daily import DailyReportQuery
from database.querys.reports.daily.mongo import MongoDailyReportQuery
from database.querys.reports.daily.postgres import PostgresDailyReportQuery