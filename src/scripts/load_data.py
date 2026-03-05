from datetime import datetime
import json
import platform
from typing import List

import pandas as pd
from sqlalchemy import Column, DateTime, MetaData, String, Table, INTEGER, UniqueConstraint, and_, inspect, schema, text, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from src.config.settings import Settings
from src.config.logger import LoggerConfig
from src.config.db import ManageDB
from src.utils.get_last_timestamp import GetLastTimestamp
from src.utils.normalize_price import NormalizePrice


class LoadData:
    def __init__(self):
        self.db_config = ManageDB()
        self.settings = Settings()
        self.get_last_timestamp = GetLastTimestamp()
        self.normalize_price = NormalizePrice()
        self.conn_string_default_DB = (
            self.settings.POSTGRES_CONNECTION_STRING_DEFAULT_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CONNECTION_STRING_DOCKER_DEFAULT_DB
        )
        self.conn_string_for_cursor_default_DB = (
            self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DEFAULT_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_DEFAULT_DB
        )
        self.engine = None
        self.conn_string_new_DB = (
            self.settings.POSTGRES_CONNECTION_STRING_NEW_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CONNECTION_STRING_DOCKER_NEW_DB
        )
        self.conn_string_for_cursor_new_DB = (
            self.settings.POSTGRES_CURSOR_CONNECTION_STRING_NEW_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_NEW_DB
        )
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    # def load(self, __data__: dict):
    #     if not __data__: 
    #         self.logger.warning("No hay datos para insertar, se omite la carga.") 
    #         return
    #     __data__["raw_data"] = __data__.pop("data")
    #     product_id = __data__.get('product_id', None)
    #     raw_product_data = __data__.get('raw_data', {})
    #     list_price_raw_data = raw_product_data.get('list_price', None)
    #     cash_price_raw_data = raw_product_data.get('cash_price', None)
    #     list_price_normalized = self.normalize_price.execute(list_price_raw_data)
    #     cash_price_normalized = self.normalize_price.execute(cash_price_raw_data)
    #     product_DB_query = f"""
    #         SELECT 
    #             * 
    #         FROM 
    #             "raw".products 
    #         WHERE
    #             product_id = '{product_id}'
    #         ORDER BY 
    #             updated_at DESC
    #         LIMIT 1
    #     """
    #     self.logger.info({
    #         "product_id": product_id, 
    #         "list_price_raw_data": list_price_raw_data,
    #         "cash_price_raw_data": cash_price_raw_data,
    #         "list_price_normalized": list_price_normalized,
    #         "cash_price_normalized": cash_price_normalized,
    #         "product_DB_query": product_DB_query
    #     })

    #     self.logger.info(f"DATA TO LOAD: {json.dumps(__data__, indent=2)}")  
    #     self.logger.info("Starting database connection and setup...")
    #     self.engine = self.db_config.create_engine(self.conn_string_default_DB)
    #     conn = self.db_config.create_connection(self.conn_string_for_cursor_default_DB)
    #     self.db_config.create_database(conn, self.settings.POSTGRES_DB_NAME_USE)
    #     conn.close()
    #     self.engine = self.db_config.create_engine(self.conn_string_new_DB)
    #     self.logger.info("Database and schema setup completed.")
    #     self.logger.info("Starting data load into database...")
    #     table_name = "scraping_data"
    #     metadata = MetaData(schema="raw")
    #     raw_products_scraping = Table(
    #         table_name,
    #         metadata,
    #         Column("id", INTEGER, primary_key=True, autoincrement=True), # Recomendado para tracking
    #         Column("scraped_at", DateTime),
    #         Column("product_id", String),
    #         Column("retailer", String),
    #         Column("raw_data", JSONB),      # El dump completo del scraper
    #         UniqueConstraint("scraped_at", "product_id", "retailer", name="uq_scraped_product_retailer")
    #     )
    #     with self.engine.begin() as conn:
    #         inspector = inspect(conn)
    #         if "raw" not in inspector.get_schema_names():
    #             conn.execute(schema.CreateSchema("raw"))
    #         metadata.create_all(conn)
    #     with self.engine.begin() as conn:
    #         stmt = insert(raw_products_scraping).values(__data__)
    #         stmt = stmt.on_conflict_do_nothing(
    #             index_elements=["scraped_at", "product_id", "retailer"]
    #         )
    #         with self.engine.begin() as conn:
    #             conn.execute(stmt)
    #         self.logger.info(
    #             f"Data successfully loaded into table: raw.{table_name} (duplicates ignored)"
    #         )
    #     self.logger.info("Data load process completed.")

    def load(self, __data__: dict):
        if not __data__: 
            self.logger.warning("No hay datos para insertar, se omite la carga.") 
            return

        # Preparar datos
        __data__["raw_data"] = __data__.pop("data")
        product_id = __data__.get('product_id', None)
        retailer = __data__.get('retailer', None)
        raw_product_data = __data__.get('raw_data', {})

        # Normalizar precios
        list_price_raw_data = raw_product_data.get('list_price', None)
        cash_price_raw_data = raw_product_data.get('cash_price', None)
        list_price_normalized = self.normalize_price.execute(list_price_raw_data)
        cash_price_normalized = self.normalize_price.execute(cash_price_raw_data)

        # Log inicial
        self.logger.info({
            "product_id": product_id, 
            "list_price_raw_data": list_price_raw_data,
            "cash_price_raw_data": cash_price_raw_data,
            "list_price_normalized": list_price_normalized,
            "cash_price_normalized": cash_price_normalized
        })
        self.logger.info(f"DATA TO LOAD: {json.dumps(__data__, indent=2)}")  

        # Conexión DB
        self.logger.info("Starting database connection and setup...")
        self.engine = self.db_config.create_engine(self.conn_string_new_DB)
        self.logger.info("Database and schema setup completed.")

        # Validación contra raw.products
        product_DB_query = f"""SELECT scraped_list_price, scraped_cash_price, updated_at FROM "raw".products WHERE product_id = '{product_id}' AND retailer = '{retailer}' ORDER BY updated_at DESC LIMIT 1"""
        with self.engine.connect() as conn:
            result = conn.execute(text(product_DB_query)).fetchone()

        insert_in_products = False
        if result:
            db_list_price, db_cash_price, db_updated_at = result
            if list_price_normalized != db_list_price or cash_price_normalized != db_cash_price:
                self.logger.info(
                    f"Precio cambiado para {product_id}: "
                    f"DB(list={db_list_price}, cash={db_cash_price}) "
                    f"vs Scraped(list={list_price_normalized}, cash={cash_price_normalized})"
                )
                insert_in_products = True
            else:
                self.logger.info(f"Precios sin cambios para {product_id}, se omite inserción en raw.products.")
        else:
            self.logger.info(f"No existe producto previo en raw.products para {product_id}, se insertará nuevo registro.")
            insert_in_products = True

        # Definir tabla raw.scraping_data
        table_name = "scraping_data"
        metadata = MetaData(schema="raw")
        raw_products_scraping = Table(
            table_name,
            metadata,
            Column("id", INTEGER, primary_key=True, autoincrement=True),
            Column("scraped_at", DateTime),
            Column("product_id", String),
            Column("retailer", String),
            Column("raw_data", JSONB),
            UniqueConstraint("scraped_at", "product_id", "retailer", name="uq_scraped_product_retailer")
        )

        # Crear esquema y tabla si no existen
        with self.engine.begin() as conn:
            inspector = inspect(conn)
            if "raw" not in inspector.get_schema_names():
                conn.execute(schema.CreateSchema("raw"))
            metadata.create_all(conn)

        # # Insertar en raw.scraping_data
        # with self.engine.begin() as conn:
        #     stmt = insert(raw_products_scraping).values(__data__)
        #     stmt = stmt.on_conflict_do_nothing(
        #         index_elements=["scraped_at", "product_id", "retailer"]
        #     )
        #     conn.execute(stmt)
        # self.logger.info(f"Data successfully loaded into table: raw.{table_name} (duplicates ignored)")

        if insert_in_products:
            products_table = Table("products", metadata, autoload_with=self.engine)

            # Insertar en raw.scraping_data
            with self.engine.begin() as conn:
                stmt = insert(raw_products_scraping).values(__data__)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["scraped_at", "product_id", "retailer"]
                )
                conn.execute(stmt)
            self.logger.info(f"Data successfully loaded into table: raw.{table_name} (duplicates ignored)")

            with self.engine.begin() as conn:
                stmt = (
                    update(products_table)
                    .where(and_( products_table.c.product_id == product_id, products_table.c.retailer == retailer ))
                    .values(
                        scraped_list_price=list_price_normalized,
                        scraped_cash_price=cash_price_normalized,
                        updated_at=datetime.now()
                    )
                )
                result = conn.execute(stmt)

                # Si no se actualizó ninguna fila (producto no existe), podés insertar
                if result.rowcount == 0:
                    new_product_entry = {
                        "product_id": product_id,
                        "scraped_list_price": list_price_normalized,
                        "scraped_cash_price": cash_price_normalized,
                        "updated_at": datetime.now()
                    }
                    conn.execute(insert(products_table).values(new_product_entry))

            self.logger.info(f"Registro scrapeado de Producto {product_id} actualizado/insertado en raw_products_scraping")
            self.logger.info(f"Producto {product_id} actualizado/insertado en raw.products.")

        self.logger.info("Data load process completed.")

    def create_scraping_error_logs_table(self):
        scraping_error_logs_table_query = f""" 
            CREATE TABLE IF NOT EXISTS logs.scraping_error_logs ( 
                id SERIAL PRIMARY KEY, 
                log_time DATE NOT NULL, 
                product_id VARCHAR(100), 
                retailer VARCHAR(100), 
                field VARCHAR(100),
                error JSONB NOT NULL,
                CONSTRAINT uq_scraping_error UNIQUE (log_time, product_id, retailer, field)
            ); 
        """ 
        conn = self.db_config.create_connection(self.conn_string_for_cursor_default_DB)
        self.db_config.create_database(conn, self.settings.POSTGRES_DB_NAME_USE)
        conn_new_db = self.db_config.create_connection(self.conn_string_for_cursor_new_DB)
        self.db_config.create_schema(conn_new_db, "logs")
        cursor_new_db = conn_new_db.cursor()
        cursor_new_db.execute(scraping_error_logs_table_query)
        conn_new_db.commit()
        self.logger.info("Table logs.scraping_error_logs was created succesfully")

    def load_scraping_error_logs(self, product_id, retailer, exception, message, by, path, field):
        self.engine = self.db_config.create_engine(self.conn_string_new_DB)
        metadata = MetaData(schema="logs") 
        scraping_error_logs = Table("scraping_error_logs", metadata, autoload_with=self.engine)
        error_entry = { 
            "log_time": datetime.now().date(), 
            "product_id": product_id, 
            "retailer": retailer, 
            "field": field,
            "error": { 
                "exception": exception, 
                "message": message, 
                "by": by, 
                "path": path 
            } 
        }
        with self.engine.begin() as conn: 
            stmt = insert(scraping_error_logs).values(error_entry) 
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["log_time", "product_id", "retailer", "field"]
            )
            conn.execute(stmt)