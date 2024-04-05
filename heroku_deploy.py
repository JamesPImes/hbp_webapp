"""
Create app instance for Heroku deployment.
"""

from app import create_app, CONFIGS

app = create_app(CONFIGS["PROD"])


if __name__ == "__main__":
    app.run()
