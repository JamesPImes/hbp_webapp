"""
Create app instance for deployment.
"""

from create_app import Config, create_app


app = create_app(Config())

if __name__ == "__main__":
    app.run()
