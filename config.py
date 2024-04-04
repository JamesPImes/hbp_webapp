import os

import dotenv


dotenv.load_dotenv()


class Config:
    ENVIRONMENT_SHORT_NAME = "NOT_DEFINED"

    def __init__(self):
        """
        Each config subclass will fill in the environment strings as
        ``'MONGO_CONNECTION_STRING_PROD'`` (for a config subclass whose
        ``.ENVIRONMENT_SHORT_NAME=='PROD'``), etc.
        """
        self.MONGO_CONNECTION_STRING = os.environ.get(f"MONGO_CONNECTION_STRING_{self.ENVIRONMENT_SHORT_NAME}")
        self.MONGO_URI = os.environ.get(f"MONGO_URI_{self.ENVIRONMENT_SHORT_NAME}")
        self.MONGO_USER = os.environ.get(f"MONGO_USERNAME_{self.ENVIRONMENT_SHORT_NAME}")
        self.MONGO_PASS = os.environ.get(f"MONGO_PASS_{self.ENVIRONMENT_SHORT_NAME}")
        self.DATABASE_NAME = os.environ.get(f"DATABASE_NAME_{self.ENVIRONMENT_SHORT_NAME}")
        self.WELL_RECORDS_COLLECTION = os.environ.get(f"WELL_RECORDS_COLLECTION_{self.ENVIRONMENT_SHORT_NAME}")


class DevelopmentConfig(Config):
    ENVIRONMENT_SHORT_NAME = "DEV"


class ProductionConfig(Config):
    ENVIRONMENT_SHORT_NAME = "PROD"


class TestingConfig(Config):
    ENVIRONMENT_SHORT_NAME = "TEST"
