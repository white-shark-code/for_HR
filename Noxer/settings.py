from enum import Enum

from pydantic_settings import BaseSettings


class DatabaseType(Enum):
    POSTGRESQL: str = "postgresql"
    SQLITE: str = "sqlite"
    MYSQL: str = "mysql"
    MARIADB: str = "mariadb"

    @property
    def async_driver(self):
        async_driver_dict: dict[DatabaseType, str] = {
            "postgresql": "postgresql+asyncpg",
            "sqlite": "sqlite+aiosqlite",
            "mysql": "mysql+aiomysql",
            "mariadb": "mariadb+asyncmy",
        }

        return async_driver_dict.get(self.value)

    @property
    def sync_driver(self):
        sync_driver_dict: dict[DatabaseType, str] = {
            "postgresql": "postgresql+psycopg2",
            "sqlite": "sqlite",
            "mysql": "mysql+mysqldb",
            "mariadb": "mariadb+mariadbconnector",
        }

        return sync_driver_dict.get(self.value)


class MainCFG(BaseSettings):
    DEBUG: bool = True
    DB_TYPE: DatabaseType
    DB_PATH: str
    UPDATE_HOURS: int
    REDIS_URL: str

    @property
    def DATABASE_URL_SYNC_ENGINE(self):
        url: str = f"{self.DB_TYPE.sync_driver}://{self.DB_PATH}"
        return url

    @property
    def DATABASE_URL_ASYNC_ENGINE(self):
        url: str = f"{self.DB_TYPE.async_driver}://{self.DB_PATH}"
        if self.DB_TYPE == DatabaseType.SQLITE:
            url += "?check_same_thread=False"
        return url


cfg: MainCFG = MainCFG(_env_file='./.env')
