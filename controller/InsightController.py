#InsightExtractor/InsightController/ingest.py

from flask import Blueprint, request, jsonify, current_app
from service.InsightService import ingest_feed_url, get_theme_by_id, get_all_themes
ingest_bp = Blueprint('ingest', __name__)
theme_bp = Blueprint('themes', __name__)
@ingest_bp.route('/ingest', methods=['POST'])
def ingest_route():
    data = request.get_json() or {}
    feed_url = data.get('feed_url')
    if not feed_url:
        return jsonify({"error": "Missing 'feed_url'"}), 400
    try:
        ingest_feed_url(feed_url)
    except Exception as e:
        # Unexpected server error—log and respond with generic message
        current_app.logger.error(f"Error ingesting feed {feed_url}", exc_info=True)
        return jsonify({"error": "Internal error during ingestion"}), 500
    return jsonify({"Status": "Success"}), 200



@theme_bp.route('/themes', methods=['GET'])
def list_themes():
    try:
        themes = get_all_themes()
        if( themes.len() ) == 0:
            return jsonify({"error": "No themes found"}), 404
    except Exception as e:
        current_app.logger.error("Error retrieving themes ", exc_info=True)
        return jsonify({"error": "Internal error during theme fetching"}), 500
    return jsonify(themes), 200

@theme_bp.route('/themes/<int:theme_id>', methods=['GET'])
def get_theme(theme_id):
    try:
        theme = get_theme_by_id(theme_id)
        if theme:
            return jsonify(theme), 200
        return jsonify({"error": "Theme not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving theme with id {id}", exc_info=True)
        return jsonify({"error": "Internal error during theme fetching"}), 500
