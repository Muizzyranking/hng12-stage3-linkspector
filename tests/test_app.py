from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_integration_json():
    """
    Test that the /integrations-json endpoint returns the expected integration specification.
    """
    response = client.get("/integrations.json")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    integration_data = data["data"]
    assert "descriptions" in integration_data
    assert "settings" in integration_data
    assert isinstance(integration_data["settings"], list)


def test_tick_endpoint():
    """
    Test that the /tick endpoint starts the
    monitoring task and returns a 202 status code.
    """
    payload = {
        "channel_id": "test-channel",
        "return_url": "http://example.com/return",
        "settings": [
            {
                "label": "root_url",
                "type": "text",
                "required": True,
                "default": "https://example.com",
                "description": "The root URL of the website to crawl",
            },
            {
                "label": "crawl_depth",
                "type": "number",
                "required": True,
                "default": "2",
                "description": "Maximum depth to crawl for internal links",
            },
            {
                "label": "required_meta_tags",
                "type": "text",
                "required": True,
                "default": "title,meta description",
                "description": "Comma-separated list of required meta tags",
            },
        ],
    }
    response = client.post("/tick", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data.get("message") == "Task scheduled"
