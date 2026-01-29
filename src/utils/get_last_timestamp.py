from sqlalchemy import DateTime, cast, func, inspect, select

class GetLastTimestamp:
    @classmethod
    def execute(cls, engine, table):
        """Obtiene el timestamp más reciente de la tabla raw."""
        inspector = inspect(engine)
        if table.name not in inspector.get_table_names():
            return None
        with engine.connect() as conn:
            stmt = select(func.max(cast(table.c.data['timestamp'].as_string(), DateTime)))
            return conn.scalar(stmt)