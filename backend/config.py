from orjson import dumps, loads, OPT_INDENT_2
from pydantic import BaseModel

from os import urandom
from typing import Optional


class MongoDBConfig(BaseModel):
    uri: str = "mongodb+srv://username:password@example.com/db_name"
    db_name: str = "db_name"
    use_tls: bool = False
    tls_cafile: Optional[str] = None


class Config(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    instance_id: int = 0
    jwt_key: str = urandom(16).hex()
    mongodb: MongoDBConfig = MongoDBConfig()


try:
    with open("config.json", "rb") as config_file:
        config = Config(**loads(config_file.read()))
except:
    default_config = Config()
    with open("config.json", "wb") as config_file:
        config_file.write(dumps(
            default_config.model_dump(),
            option=OPT_INDENT_2
        ))
    print("Config file not found, auto generate a new config file...")
    exit(0)

with open("config.json", "wb") as config_file:
    config_file.write(dumps(
        config.model_dump(),
        option=OPT_INDENT_2
    ))

HOST = config.host
PORT = config.port
INSTANCE_ID = config.instance_id
JWT_KEY = config.jwt_key

MONGODB_URI = config.mongodb.uri
MONGODB_DB_NAME = config.mongodb.db_name
MONGODB_USE_TLS = config.mongodb.use_tls
MONGODB_CA_FILE = config.mongodb.tls_cafile
