# NOTA: DAILY_SUMMARY_SCHEMA y HOUR_SUMMARY_SCHEMA existen tanto en
# schemas.bbip.ip.summaries como en schemas.bbip.traffic.summaries con el
# mismo nombre. No se re-exportan aqui para evitar que una pise a la otra;
# se siguen importando por su ruta especifica en cada modulo que las usa.

from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip import (
    IP_HISTORY_SCHEMA,
    SOURCE_IP_BBIP_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic import (
    BBIP_TRAFFIC_SCHEMA,
    SOURCE_TRAFFIC_BBIP_SCHEMA,
)

__all__ = [
    "IP_HISTORY_SCHEMA",
    "SOURCE_IP_BBIP_SCHEMA",
    "BBIP_TRAFFIC_SCHEMA",
    "SOURCE_TRAFFIC_BBIP_SCHEMA",
]
