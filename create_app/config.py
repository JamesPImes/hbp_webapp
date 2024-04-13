import os

import dotenv

dotenv.load_dotenv()


class Config:
    # Only MongoDB is currently supported, but in case we want to use a
    # different database in the future, allow this to be configured.
    DATABASE_PROGRAM = os.environ.get("DATABASE_PROGRAM")
    DATABASE_CONNECTION_STRING = os.environ.get(f"DATABASE_CONNECTION_STRING")
    DATABASE_NAME = os.environ.get(f"DATABASE_NAME")
    WELL_RECORDS_COLLECTION = os.environ.get(f"WELL_RECORDS_COLLECTION")
    MAX_RECORD_AGE_IN_DAYS = 27
    # Configure how date ranges appear.
    #   '01-01-2020 :: 12-31-2020 (366 days; 12 calendar months)'
    BETWEEN_DATES = " :: "
    SHOW_DAYS_IN_DATE_RANGES = True
    SHOW_MONTHS_IN_DATE_RANGES = True
