from database.schemas.borde import BORDE_SCHEMA as BORDE_SCHEMA_MONGO
from database.schemas.bras import BRAS_SCHEMA as BRAS_SCHEMA_MONGO
from database.schemas.caching import CACHING_SCHEMA as CACHING_SCHEMA_MONGO
from database.schemas.rai import RAI_SCHEMA as RAI_SCHEMA_MONGO
from database.schemas.ipHistory import IP_HISTORY_SCHEMA as IP_HISTORY_SCHEMA_MONGO
from database.schemas.dailyReport import DAILY_REPORT_SCHEMA as DAILY_REPORT_SCHEMA_MONGO
from database.libs.product.database import Database
from database.libs.product.mongo import DatabaseMongo
from database.libs.factory.database import DatabaseFactory
from database.libs.factory.mongo import DatabaseMongoFactory
from database.querys.bbip.query import BBIPQuery
from database.querys.daily.query import DailyReportQuery
from database.querys.bbip.borde import BordeMongoQuery
from database.querys.bbip.bras import BrasMongoQuery
from database.querys.bbip.caching import CachingMongoQuery
from database.querys.bbip.rai import RaiMongoQuery
from database.querys.daily.daily import DailyReportMongoQuery