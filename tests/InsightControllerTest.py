import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from controller.InsightController import ingest_bp, theme_bp

class IngestControllerTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(ingest_bp)
        app.register_blueprint(theme_bp)
        self.client = app.test_client()

    @patch('controller.InsightController.ingest_bp')
    def test_ingest_route_success(self, mock_ingest_feed_url):
        mock_ingest_feed_url.return_value = None

        response = self.client.post('/ingest', json={'feed_url': 'http://example.com/feed'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"Status": "Success"})

if __name__ == '__main__':
    unittest.main()
