# tests/test_service.py
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import numpy as np
import pytest
from service.InsightService import ingest_feed_url, get_all_themes, get_theme_by_id


@pytest.fixture
def mock_feed_entry():
    return {
        'link': 'http://example.com/post1',
        'title': 'Sample Post',
        'summary': 'This is a sample post.',
        'published_parsed': (2025, 6, 16, 12, 0, 0, 0, 0, 0)
    }
def test_ingest_feed_url_success(mocker, mock_feed_entry):
    # Mock feedparser response

    mock_feedparser = mocker.patch('service.InsightService.feedparser.parse')
    mock_feedparser.return_value.entries = [mock_feed_entry]

    # Mock model encoding
    mock_model = mocker.patch('service.InsightService.model.encode')
    mock_model.return_value = [np.array([0.1, 0.2, 0.3])]
    # Mock cosine similarity
    mock_cosine = mocker.patch('service.InsightService.cosine_similarity')
    mock_cosine.return_value = [[0.5]]  # Below SIM_THRESHOLD to trigger new theme creation

    # Mock database session
    mock_session = mocker.patch('service.InsightService.Session')
    mock_session_instance = mock_session.return_value.__enter__.return_value

    # Mock no duplicate post
    mock_session_instance.exec.return_value.first.return_value = None

    # Mock theme query to return one existing theme (triggers cosine_similarity)
    mock_session_instance.exec.return_value.all.return_value = [
        MagicMock(embedding=json.dumps([0.4, 0.5, 0.6]))
    ]
    # Mock commit to simply pass
    mock_session_instance.commit = MagicMock()

    # Call the service function
    ingest_feed_url('http://example.com/feed')

    # Assertions
    assert mock_feedparser.called
    assert mock_model.called
    assert mock_cosine.called
    assert mock_session_instance.add.call_count == 2  # One for theme, one for post
    assert mock_session_instance.commit.call_count == 2  # Once for theme, once for post


def test_get_all_themes_success(mocker):
    # Mock database session
    mock_session = mocker.patch('service.InsightService.Session')
    mock_session_instance = mock_session.return_value.__enter__.return_value

    # Prepare mock query results
    mock_results = [
        (1, "Thesis A", 3),
        (2, "Thesis B", 5),
    ]

    # Mock session.exec(statement).all()
    mock_session_instance.exec.return_value.all.return_value = mock_results

    # Call the service function
    themes = get_all_themes()

    # Assertions
    assert themes == [
        {"id": 1, "thesis_text": "Thesis A", "post_count": 3},
        {"id": 2, "thesis_text": "Thesis B", "post_count": 5},
    ]

    assert mock_session.called
    assert mock_session_instance.exec.called

def test_get_theme_by_id_success(mocker):
    # Mock database session
    mock_session = mocker.patch('service.InsightService.Session')
    mock_session_instance = mock_session.return_value.__enter__.return_value

    # Prepare mock theme
    mock_theme = mocker.Mock()
    mock_theme.id = 1
    mock_theme.thesis_text = "Sample Thesis"

    # Prepare mock posts
    mock_post = mocker.Mock()
    mock_post.id = 101
    mock_post.post_title = "Sample Post"
    mock_post.post_url = "http://example.com/post"
    mock_post.published_at = datetime(2025, 6, 16, 12, 0, 0, tzinfo=timezone.utc)
    mock_post.thesis_text = "Sample Post Thesis"

    # Setup session.get to return the mock theme
    mock_session_instance.get.return_value = mock_theme

    # Setup session.exec(statement).all() to return mock posts
    mock_session_instance.exec.return_value.all.return_value = [mock_post]

    # Call the service function
    result = get_theme_by_id(1)

    # Expected response
    expected = [{
        "id": 1,
        "thesis_text": "Sample Thesis",
        "posts": [
            {
                "id": 101,
                "title": "Sample Post",
                "url": "http://example.com/post",
                "published_at": "2025-06-16T12:00:00+00:00",
                "thesis_text": "Sample Post Thesis",
            }
        ],
    }]

    # Assertions
    assert result == expected
    assert mock_session_instance.get.called
    assert mock_session_instance.exec.called



