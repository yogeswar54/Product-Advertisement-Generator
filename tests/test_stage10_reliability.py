from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

def test_stage10_database_endpoint_failure_is_clean(api_client):
    with patch("app.api.routes.campaign_history._campaign_or_404", side_effect=RuntimeError("database locked")):
        response = api_client.get("/campaigns/missing")
    assert response.status_code == 500
    assert "database locked" not in response.text.lower()


def test_stage10_light_concurrency_does_not_mix_results(api_client):
    def fetch():
        return api_client.get("/campaigns").status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        statuses = list(pool.map(lambda _: fetch(), range(10)))
    assert statuses == [200] * 10


def test_stage10_health_has_no_internal_error(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert "traceback" not in response.text.lower()
