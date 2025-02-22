from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse

from app.models import MonitorPayload
from app.tasks import task

router = APIRouter()


@router.get("/integrations.json")
def integration_spec(request: Request):
    base_url = "https://3sgxzpc6-8000.uks1.devtunnels.ms"
    # base_url = str(request.base_url).rstrip("/")
    integration_json = {
        "data": {
            "date": {"created_at": "2025-02-09", "updated_at": "2025-02-09"},
            "descriptions": {
                "app_name": "Linkspector",
                "app_description": (
                    "Monitors internal website links and meta\
                    tags for SEO health."
                ),
                "app_logo": f"{base_url}/logo",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "is_active": True,
            "integration_type": "interval",
            "key_features": [
                "Checks for broken internal links.",
                "Monitors essential meta tags (e.g., title, meta).",
            ],
            "integration_category": "Monitoring & Logging",
            "author": "Muiz Oyebowale",
            "website": base_url,
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
                    "description": (
                        "Maximum depth to crawl for internal links."
                    ),
                },
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "description": "The first site to monitor",
                    "default": "* * * * *",
                },
                {
                    "label": "required_meta_tags",
                    "type": "text",
                    "required": True,
                    "default": "title,meta description",
                    "description": (
                        "Comma-separated list of required meta tags\
                        (e.g., title,meta description)"
                    ),
                },
            ],
            "target_url": base_url,
            "tick_url": f"{base_url}/tick",
        }
    }
    return integration_json


@router.get("/logo")
def get_logo():
    return FileResponse("assets/linkspector.png")


@router.post("/tick")
async def tick(payload: MonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(task, payload)
    return {"message": "Task scheduled"}
