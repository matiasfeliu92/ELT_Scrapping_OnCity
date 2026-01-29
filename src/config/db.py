from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2 import sql, OperationalError

from src.config.logger import LoggerConfig

class ManageDB:
    def __init__(cls):
        cls.logger = LoggerConfig.get_logger(cls.__class__.__name__)

    def create_engine(cls, __conn_string__):
        try:
            cls.engine = create_engine(__conn_string__)
            with cls.engine.connect() as connection:
                print("CONNECTION ESTABISH SUCCESSFULLY")
            return cls.engine
        except SQLAlchemyError as e:
            cls.logger.error("THERE WAS AN ERROR WITH CONNECTION \n", str(e))

    def create_connection(cls, __conn_string_for_cursor__):
        cls.logger.info(f"Creating connection with connection string: {__conn_string_for_cursor__}")
        try:
            conn = psycopg2.connect(__conn_string_for_cursor__)
            conn.autocommit = True
            print("CONNECTION ESTABISH SUCCESSFULLY")
            return conn
        except psycopg2.Error as ex:
            cls.logger.error(f"Error al conectar: {ex}")

    def create_database(cls, __conn__, __db_name__):
        try:
            with __conn__.cursor() as cur:
                cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [__db_name__])
                if cur.fetchone():
                    cls.logger.warning(f"ℹ️ La base de datos '{__db_name__}' ya existe.")
                else:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(__db_name__)))
                    cls.logger.info(f"✅ Base de datos '{__db_name__}' creada correctamente.")
        except Exception as e:
            cls.logger.error(f"❌ Error al crear la base de datos: {e}")

    def create_schema(cls, __conn__, __schema_name__):
        try:
            with __conn__.cursor() as cur:             
                cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(__schema_name__)))
                cls.logger.info(f"✅ Nuevo schema '{__schema_name__}' creado correctamente.")
        except Exception as e:
            cls.logger.error(f"❌ Error al crear el schema: {e}")