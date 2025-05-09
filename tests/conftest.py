import pytest


@pytest.fixture
def mock_thredds_url_root(monkeypatch):
    monkeypatch.setenv(
        "THREDDS_URL_ROOT",
        "https://marble-dev01.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets",
    )
