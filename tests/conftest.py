import pytest
from app import create_app
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()