import pytest
from flask import Flask
from controller.InsightController import ingest_bp, theme_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(ingest_bp)
    app.register_blueprint(theme_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_ingest_route_success(client, mocker):
    mocker.patch('controller.InsightController.ingest_bp', return_value=None)
    response = client.post('/ingest', json={'feed_url': 'http://example.com/feed'})
    assert response.status_code == 200
    assert response.get_json() == {"Status": "Success"}

def test_ingest_route_400(client,mocker):
    mocker.patch('controller.InsightController.ingest_bp', return_value=None)
    response = client.post('/ingest', json={})  # feed_url missing entirely
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing feed_url"}

def test_ingest_route_failure(client, mocker):
    mock_ingest = mocker.patch('controller.InsightController.ingest_feed_url')
    mock_ingest.side_effect = Exception('Mocked ingestion failure')
    response = client.post('/ingest', json={'feed_url': 'http://example.com/feed'})
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal error during ingestion"}



def test_get_theme_route_success(client, mocker):
    # Patch ingest_feed_url in your controller module
    mock_ingest = mocker.patch('controller.InsightController.get_all_themes')
    mock_ingest.side_effect = [
    {
        "id": 1,
        "post_count": 1,
        "thesis_text": "Written by Sharon Wilson Purdy, Planetary Geologist at the Smithsonian National Air and Space Museum Earth planning date: Wednesday, June 11, 2025 As we near the end of our Altadena drill campaign, Curiosity continued her exploration of the Martian bedrock within the boxwork structures on Mount Sharp. After successfully delivering a powdered rock sample to […]"
    }]
    response = client.get('/themes')
    assert response.status_code == 200

def test_get_theme_route_404(client,mocker):
    mock_ingest = mocker.patch('controller.InsightController.get_all_themes')
    mock_ingest.return_value = []
    response = client.get('/themes')
    assert response.status_code == 404

def test_get_theme_failure(client, mocker):
    mock_ingest = mocker.patch('controller.InsightController.get_all_themes')
    mock_ingest.side_effect = Exception('Mocked theme fetch failure')
    response = client.get('/themes')
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal error during theme fetching"}



def test_get_theme_route_404(client,mocker):
    mock_ingest = mocker.patch('controller.InsightController.get_theme_by_id')
    mock_ingest.return_value = []
    response = client.get('/themes/1')
    assert response.status_code == 404

def test_get_theme_failure(client, mocker):
    mock_ingest = mocker.patch('controller.InsightController.get_theme_by_id')
    mock_ingest.side_effect = Exception('Mocked theme fetch failure')
    response = client.get('/themes/1')
    assert response.status_code == 500


def test_get_theme_route_success(client, mocker):
    # Patch ingest_feed_url in your controller module
    mock_ingest = mocker.patch('controller.InsightController.get_all_themes')
    mock_ingest.side_effect = [
        {
            "id": 10,
            "posts": [
                {
                    "id": 10,
                    "published_at": "2025-06-12T17:42:07",
                    "thesis_text": "A new generation of aerospace explorers will soon embark on a hands-on summer experience focusing on careers in science, mathematics, engineering, and technology (STEM). This month, NASA’s Armstrong Flight Research Center in Edwards, California, and the Flight Test Museum Foundation will launch the 2025 Junior Test Pilot School. Held at Blackbird Airpark and Joe Davies [&#8230;]",
                    "title": "NASA, Museum to Launch Junior Pilot School for Young Innovators",
                    "url": "https://www.nasa.gov/news-release/nasa-museum-to-launch-junior-pilot-school-for-young-innovators/"
                }
            ],
            "thesis_text": "A new generation of aerospace explorers will soon embark on a hands-on summer experience focusing on careers in science, mathematics, engineering, and technology (STEM). This month, NASA’s Armstrong Flight Research Center in Edwards, California, and the Flight Test Museum Foundation will launch the 2025 Junior Test Pilot School. Held at Blackbird Airpark and Joe Davies [&#8230;]"
        }
    ]
    response = client.get('/themes')
    assert response.status_code == 200

