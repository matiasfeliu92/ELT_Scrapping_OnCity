from datetime import datetime, timedelta
import os
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from src.scripts.load_data import LoadData
from src.scripts.extract_data import ExtractData
from src.config.settings import Settings
from src.utils.move_product_catalog_to_dbt_seeds import MoveXlsxToSeeds
from src.config.logger import LoggerConfig

class ProductsPipelineDAG:
    def __init__(self, dag_id, schedule_interval, start_date):
        self.settings = Settings()
        self.base_dir = self.settings.BASE_DIR
        self.move_product_catalog = MoveXlsxToSeeds()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.extract_data = ExtractData()
        self.load_data = LoadData()
        self.dag_id = dag_id
        self.schedule_interval = schedule_interval
        self.start_date = start_date
        self.default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'email': ['airflow@example.com'],
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 2,
            'retry_delay': timedelta(minutes=5),
        }

    def move_product_catalog_to_seeds(self): ## 1ERA TAREA
        self.logger.info(f"BASE DIR ----- {self.base_dir}")
        self.move_product_catalog.read_google_sheets()
        self.move_product_catalog.load_csv_in_dbt_seeds()

    def create_scraping_error_logs(self):
        self.load_data.create_scraping_error_logs_table()

    def extract_scraped_data(self):
        scraped_data = self.extract_data.extract()
        return scraped_data
    
    def load_scraped_data(self, ti):
        scraped_data = ti.xcom_pull(
            task_ids='extract_scraped_data'
        )
        if scraped_data is not None and len(scraped_data)>0:
            self.logger.info(f"Registros recibidos: {len(scraped_data)}")
            self.load_data.load(scraped_data)
        else:
            self.load_data.load([])

    def create_dag(self):
        dag = DAG(
            self.dag_id,
            default_args=self.default_args,
            description='Un DAG basado en clases',
            schedule_interval=self.schedule_interval,
            start_date=self.start_date,
            catchup=False,
        )

        with dag:
            move_product_catalog_to_seeds_ = PythonOperator(
                task_id='move_product_catalog',
                python_callable=self.move_product_catalog_to_seeds,
            )

            update_dbt_profile = BashOperator(
                task_id='update_dbt_profile',
                bash_command="""
                sed -i 's/host: localhost/host: host.docker.internal/g' \
                /opt/airflow/.dbt/profiles.yml
                """
            )

            dbt_seed = BashOperator(
                task_id='run_dbt_seed',
                bash_command=f"cd {os.path.join(self.base_dir, 'products_scraping')} && dbt seed --profiles-dir /opt/airflow/.dbt && cd {self.base_dir}"
            )

            create_scraping_error_logs_table = PythonOperator(
                task_id='create_scraping_error_logs_table',
                python_callable=self.create_scraping_error_logs,
            )

            extract_data = PythonOperator(
                task_id='extract_scraped_data',
                python_callable=self.extract_scraped_data,
            )

            load_data = PythonOperator(
                task_id='load_scraped_data',
                python_callable=self.load_scraped_data,
            )

            update_dbt_profile_to_localhost = BashOperator(
                task_id='update_dbt_profile_to_localhost',
                bash_command="""
                sed -i 's/host: host.docker.internal/host: localhost/g' \
                /opt/airflow/.dbt/profiles.yml
                """
            )

            move_product_catalog_to_seeds_ >> update_dbt_profile >> dbt_seed >> create_scraping_error_logs_table >> extract_data >> load_data >> update_dbt_profile_to_localhost

        return dag
    
products_pipeline = ProductsPipelineDAG(
    dag_id='products_pipeline_DAG',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1)
)

# Airflow lee esta variable global
dag = products_pipeline.create_dag()