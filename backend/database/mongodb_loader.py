import os

import dotenv
from pymongo import MongoClient

dotenv.load_dotenv()


def get_mongo_client_for_environment(environment: str) -> MongoClient:
    """
    Get a ``MongoClient`` that has been configured in ``.env`` for the
    specified environment (``'PROD'``, ``'DEV'``, or ``'TEST'``; or
    another environment category specified in the ``.env`` file -- see
    ``.env.example`` for details).

    :param environment: ``'PROD'``, ``'DEV'``, ``'TEST'``, etc. (Will
     raise an ``EnvironmentError`` if the necessary environment
     variables for this environment are not specified in the ``.env``
     file.)
    :return: The configured ``MongoClient``.
    """
    connection_string = os.environ.get(f"MONGO_CONNECTION_STRING_{environment}")
    if connection_string is None:
        uri = os.environ.get(f"MONGO_URI_{environment}")
        if uri is None:
            raise EnvironmentError(
                f"Specify MONGO_CONNECTION_STRING_{environment} env variable, "
                f"or MONGO_URI_{environment} and corresponding user/pass env variables."
            )
        connection_string = uri.format(
            username=os.environ.get(f"MONGO_USERNAME_{environment}"),
            password=os.environ.get(f"MONGO_PASSWORD_{environment}"),
        )
    return MongoClient(connection_string)


__all__ = [
    "get_mongo_client_for_environment",
]
