from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from config import CONFIG

from database.mongo.schemas import (
    Competitor,
    Snapshot,
    Change,
    Announcement,
    Report,
)

class DatabaseManager:
    def __init__(self) -> None:
        self.client = MongoClient(CONFIG.MONGO_URI)
        self.db = self.client["FeaturePulse"]

        # Collections
        self.competitors = self.db["Competitors"]
        self.snapshots = self.db["Snapshots"]
        self.changes = self.db["Changes"]
        self.announcements = self.db["Announcements"]
        self.reports = self.db["Reports"]

    # ----------------------------
    # Competitors
    # ----------------------------
    def add_competitor(self, competitor: Competitor) -> str:
        data = competitor.model_dump()
        result = self.competitors.insert_one(data)
        return str(result.inserted_id)

    def get_competitors(self) -> List[dict]:
        docs = list(self.competitors.find({}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Snapshots
    # ----------------------------
    def add_snapshot(self, snapshot: Snapshot) -> str:
        data = snapshot.model_dump()
        result = self.snapshots.insert_one(data)
        return str(result.inserted_id)

    def get_snapshots(self, competitor_id: str) -> List[dict]:
        docs = list(self.snapshots.find({"competitor_id": competitor_id}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Changes
    # ----------------------------
    def add_change(self, change: Change) -> str:
        data = change.model_dump()
        result = self.changes.insert_one(data)
        return str(result.inserted_id)

    def get_changes(self, competitor_id: str) -> List[dict]:
        docs = list(self.changes.find({"competitor_id": competitor_id}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Announcements
    # ----------------------------
    def add_announcement(self, announcement: Announcement) -> str:
        data = announcement.model_dump()
        result = self.announcements.insert_one(data)
        return str(result.inserted_id)

    def get_announcements(self, competitor_id: str) -> List[dict]:
        docs = list(self.announcements.find({"competitor_id": competitor_id}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Reports
    # ----------------------------
    def add_report(self, report: Report) -> str:
        data = report.model_dump()
        result = self.reports.insert_one(data)
        return str(result.inserted_id)

    def get_reports(self) -> List[dict]:
        docs = list(self.reports.find({}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs