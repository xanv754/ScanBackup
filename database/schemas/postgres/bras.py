from constants import BrasType
from database import TableNameDatabase, BrasFieldDatabase


BRAS_SECUENCE_SCHEMA = f"""
    CREATE SEQUENCE IF NOT EXISTS {TableNameDatabase.BRAS}_id_seq
        INCREMENT BY 1
        START WITH 1
        NO CYCLE
"""


BRAS_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.BRAS} (
        {BrasFieldDatabase.ID} INTEGER PRIMARY KEY DEFAULT NEXTVAL('{TableNameDatabase.BORDE}_id_seq'),
        {BrasFieldDatabase.NAME} VARCHAR(100) NOT NULL,
        {BrasFieldDatabase.TYPE} VARCHAR(15) NOT NULL,
        {BrasFieldDatabase.CAPACITY} SMALLINT NOT NULL,
        {BrasFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
        CONSTRAINT type_bras CHECK (
            {BrasFieldDatabase.TYPE} IN (
                '{BrasType.UPLINK}',
                '{BrasType.DOWNLINK}'
            )
        ),
        CONSTRAINT {TableNameDatabase.BRAS}_unique UNIQUE ({BrasFieldDatabase.NAME}, {BrasFieldDatabase.TYPE})
    )
"""
