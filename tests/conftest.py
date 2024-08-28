import pytest


@pytest.fixture
def http_url_expect_text(httpserver):
    endpoint = "/ping"
    expected_text = "healthcheck"
    httpserver.expect_request(endpoint).respond_with_data(expected_text)
    return httpserver.url_for(endpoint), expected_text
