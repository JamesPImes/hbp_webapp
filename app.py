"""
Create app instance for deployment.
"""

import os
import dotenv
from create_app import Config, create_app

dotenv.load_dotenv()

app = create_app(Config())

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"), load_dotenv=True)
