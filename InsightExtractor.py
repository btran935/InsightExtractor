from flask import Flask,  send_file

from controller.InsightController import ingest_bp, theme_bp
from database import engine, create_db_and_tables
from service.InsightService import ingest_feed_url
from apscheduler.schedulers.background import BackgroundScheduler


FEED_URLS = [
    '"https://www.nasa.gov/rss/dyn/breaking_news.rss',
    'http://rss.cnn.com/rss/cnn_topstories.rss'
]

def schedule_feed_ingestion():
    schedule = BackgroundScheduler()

    # Schedule ingestion for each feed
    for feed_url in FEED_URLS:
        schedule.add_job(ingest_feed_url, 'interval', minutes=30, args=[feed_url])
        # This will run ingest_feed_url(feed_url) every 30 minutes

    schedule.start()
    print("Scheduler started for feed ingestion.")
    return schedule



def create_app():


    app = Flask(__name__)
    @app.route('/openapi.yaml')
    def openapi_spec():
        return send_file('openapi.yaml', mimetype='text/yaml')


    # Initialize the database tables
    create_db_and_tables()
    # Register blueprints
    app.register_blueprint(ingest_bp)
    app.register_blueprint(theme_bp)
    return app

if __name__ == '__main__':
    app = create_app()
        # Start the scheduler
    scheduler = schedule_feed_ingestion()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
            # Optional: Shut down the scheduler when the app stops
        scheduler.shutdown()
