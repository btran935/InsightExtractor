from flask import Flask

from controller.InsightController import ingest_bp, theme_bp
from database import engine, create_db_and_tables


def create_app():
    app = Flask(__name__)

    # Initialize the database tables
    create_db_and_tables()
    # Register blueprints
    app.register_blueprint(ingest_bp)
    app.register_blueprint(theme_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

