from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, HttpUrl

# ----------------------------
# Competitors Collection
# ----------------------------
class Competitor(BaseModel):
    id: Optional[str] = None  # ✅ Just string
    name: str
    website: Optional[HttpUrl] = None
    category: Optional[str] = None
    tracking_urls: List[HttpUrl] = []
    created_at: datetime = datetime.utcnow()

# ----------------------------
# Snapshots Collection
# ----------------------------
class Snapshot(BaseModel):
    id: Optional[str] = None
    competitor_id: str
    url: HttpUrl
    content_hash: str
    raw_text: str
    taken_at: datetime = datetime.utcnow()

# ----------------------------
# Changes Collection
# ----------------------------
class Change(BaseModel):
    id: Optional[str] = None
    competitor_id: str
    url: HttpUrl
    change_type: Literal["feature", "pricing", "ui", "other"]
    summary: str
    detected_at: datetime = datetime.utcnow()
    previous_hash: str
    new_hash: str

# ----------------------------
# Announcements Collection
# ----------------------------
class Announcement(BaseModel):
    id: Optional[str] = None
    competitor_id: str
    platform: Literal["twitter", "linkedin", "blog", "other"]
    content: str
    url: Optional[HttpUrl] = None
    posted_at: datetime

# ----------------------------
# Reports Collection
# ----------------------------
class Report(BaseModel):
    id: Optional[str] = None
    week: str  # e.g., "2025-W34"
    competitor_ids: List[str]
    summary: str
    delivered_to: List[str]  # email list
    delivered_at: datetime = datetime.utcnow()
