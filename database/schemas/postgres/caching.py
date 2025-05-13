from database import TableNameDatabase, CachingFieldDatabase


CACHING_SECUENCE_SCHEMA = f"""
    CREATE SEQUENCE IF NOT EXISTS {TableNameDatabase.CACHING}_id_seq
        INCREMENT BY 1
        START WITH 1
        NO CYCLE
"""


CACHING_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.CACHING} (
        {CachingFieldDatabase.ID} INTEGER PRIMARY KEY DEFAULT NEXTVAL('{TableNameDatabase.CACHING}_id_seq'),
        {CachingFieldDatabase.NAME} VARCHAR(150) NOT NULL,
        {CachingFieldDatabase.SERVICE} VARCHAR(20) NOT NULL,
        {CachingFieldDatabase.CAPACITY} REAL NOT NULL,
        {CachingFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
        CONSTRAINT {TableNameDatabase.CACHING}_unique UNIQUE ({CachingFieldDatabase.NAME}, {CachingFieldDatabase.SERVICE})
    )
"""