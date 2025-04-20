from constants.group import ModelBordeType
from storage.constant.fields import BordeFieldDatabase
from storage.constant.tables import TableNameDatabase


BORDE_SECUENCE_SCHEMA = f"""
    CREATE SEQUENCE IF NOT EXISTS {TableNameDatabase.BORDE}_id_seq
        INCREMENT BY 1
        START WITH 1
        NO CYCLE
"""


BORDE_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.BORDE} (
        {BordeFieldDatabase.ID} INTEGER PRIMARY KEY DEFAULT NEXTVAL('{TableNameDatabase.BORDE}_id_seq'),
        {BordeFieldDatabase.NAME} VARCHAR(100) NOT NULL,
        {BordeFieldDatabase.MODEL} VARCHAR(15) NOT NULL,
        {BordeFieldDatabase.CAPACITY} SMALLINT NOT NULL,
        {BordeFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
        CONSTRAINT type_model CHECK (
            {BordeFieldDatabase.MODEL} IN (
                '{ModelBordeType.CISCO}',
                '{ModelBordeType.HUAWEI}'
            )
        ),
        CONSTRAINT {TableNameDatabase.BORDE}_unique UNIQUE ({BordeFieldDatabase.NAME}, {BordeFieldDatabase.MODEL})
    )
"""
