from typing import List, Optional

from pydantic import BaseModel


class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str
    description: Optional[str] = None


class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]
