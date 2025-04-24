from database.constant.fields import RaiFieldDatabase
from database.constant.tables import TableNameDatabase


RAI_SECUENCE_SCHEMA = f"""
    CREATE SEQUENCE IF NOT EXISTS {TableNameDatabase.RAI}_id_seq
        INCREMENT BY 1
        START WITH 1
        NO CYCLE
"""


RAI_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.RAI} (
        {RaiFieldDatabase.ID} INTEGER PRIMARY KEY DEFAULT NEXTVAL('{TableNameDatabase.RAI}_id_seq'),
        {RaiFieldDatabase.NAME} VARCHAR(150) NOT NULL,
        {RaiFieldDatabase.CAPACITY} REAL NOT NULL,
        {RaiFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
        CONSTRAINT {TableNameDatabase.RAI}_unique UNIQUE ({RaiFieldDatabase.NAME})
    )
"""