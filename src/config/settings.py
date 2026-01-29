import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR = os.getcwd()
    POSTGRES_DB_USER = os.getenv("DB_USER")
    POSTGRES_DB_PASS = os.getenv("DB_PASS")
    POSTGRES_DB_HOST = os.getenv("DB_HOST")
    POSTGRES_DB_HOST_DOCKER = os.getenv("DB_HOST_DOCKER")
    POSTGRES_DB_NAME = os.getenv("DB_NAME")
    POSTGRES_DB_NAME_USE = os.getenv("DB_NAME_USE")
    POSTGRES_DB_SCHEMA_RAW = os.getenv("DB_SCHEMA_RAW")
    POSTGRES_CONNECTION_STRING_DEFAULT_DB = (
        f"postgresql+psycopg2://{POSTGRES_DB_USER}:{POSTGRES_DB_PASS}"
        f"@{POSTGRES_DB_HOST}:5432/{POSTGRES_DB_NAME}"
    )
    POSTGRES_CONNECTION_STRING_DOCKER_DEFAULT_DB = (
        f"postgresql+psycopg2://{POSTGRES_DB_USER}:{POSTGRES_DB_PASS}"
        f"@{POSTGRES_DB_HOST_DOCKER}:5432/{POSTGRES_DB_NAME}"
    )
    POSTGRES_CURSOR_CONNECTION_STRING_DEFAULT_DB = (
        "dbname={db} user={user} password={pwd} host={host} port={port}"
    ).format(
        db=POSTGRES_DB_NAME,
        user=POSTGRES_DB_USER,
        pwd=POSTGRES_DB_PASS,
        host=POSTGRES_DB_HOST,
        port=5432,
    )
    POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_DEFAULT_DB = (
        "dbname={db} user={user} password={pwd} host={host} port={port}"
    ).format(
        db=POSTGRES_DB_NAME,
        user=POSTGRES_DB_USER,
        pwd=POSTGRES_DB_PASS,
        host=POSTGRES_DB_HOST_DOCKER,
        port=5432,
    )

    POSTGRES_CONNECTION_STRING_NEW_DB = (
        f"postgresql+psycopg2://{POSTGRES_DB_USER}:{POSTGRES_DB_PASS}"
        f"@{POSTGRES_DB_HOST}:5432/{POSTGRES_DB_NAME_USE}"
    )
    POSTGRES_CONNECTION_STRING_DOCKER_NEW_DB = (
        f"postgresql+psycopg2://{POSTGRES_DB_USER}:{POSTGRES_DB_PASS}"
        f"@{POSTGRES_DB_HOST_DOCKER}:5432/{POSTGRES_DB_NAME_USE}"
    )
    POSTGRES_CURSOR_CONNECTION_STRING_NEW_DB = (
        "dbname={db} user={user} password={pwd} host={host} port={port}"
    ).format(
        db=POSTGRES_DB_NAME_USE,
        user=POSTGRES_DB_USER,
        pwd=POSTGRES_DB_PASS,
        host=POSTGRES_DB_HOST,
        port=5432,
    )
    POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_NEW_DB = (
        "dbname={db} user={user} password={pwd} host={host} port={port}"
    ).format(
        db=POSTGRES_DB_NAME_USE,
        user=POSTGRES_DB_USER,
        pwd=POSTGRES_DB_PASS,
        host=POSTGRES_DB_HOST_DOCKER,
        port=5432,
    )

    @classmethod 
    def get_dir(cls, *args) -> str: 
        path = cls.BASE_DIR 
        for value in args: 
            path = os.path.join(path, value) 
        return path
    
    @classmethod
    def create_dir(cls, *args):
        print(f"DIR PATHS ----> {args}")
        base_dir = cls.BASE_DIR
        new_path = '\\'.join(args)
        new_dir = os.path.join(base_dir, new_path)
        print(f"NEW DIR ------> {new_dir}")
        os.makedirs(new_dir, exist_ok=True)
        return new_dir