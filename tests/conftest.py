import tempfile, os
import pytest
from app import create_app


@pytest.fixture
def app():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    application = create_app({
        "TESTING": True,
        "DB_PATH": path,
        "SENHA": "segredo",
        "SECRET_KEY": "test-key",
    })
    yield application
    os.unlink(path)


@pytest.fixture
def client(app):
    return app.test_client()
