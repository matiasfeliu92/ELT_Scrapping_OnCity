from sqlalchemy import DateTime, cast, func, inspect, select

class GetLastTimestamp:
    @classmethod
    def execute(cls, engine, table):
        print(table.name)
        """Obtiene el timestamp más reciente de la tabla raw."""
        inspector = inspect(engine)
        if table.name not in inspector.get_table_names(schema=table.schema):
            print(True)
            return None
        with engine.connect() as conn:
            stmt = select(func.max(table.c.scraped_at))
            return conn.scalar(stmt)