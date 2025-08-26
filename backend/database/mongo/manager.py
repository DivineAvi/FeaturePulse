from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic.networks import HttpUrl
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
        
        # Test connection
        try:
            self.client.admin.command('ping')
            print("DEBUG: MongoDB connection successful")
        except Exception as e:
            print(f"DEBUG: MongoDB connection failed: {e}")

    def _convert_urls_to_strings(self, data: dict) -> dict:
        """Convert HttpUrl objects to strings for MongoDB storage"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, HttpUrl):
                converted[key] = str(value)
            elif isinstance(value, list):
                converted[key] = [str(item) if isinstance(item, HttpUrl) else item for item in value]
            else:
                converted[key] = value
        return converted

    # ----------------------------
    # Competitors
    # ----------------------------
    def add_competitor(self, competitor: Competitor) -> str:
        data = competitor.model_dump()
        data = self._convert_urls_to_strings(data)
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
        data = self._convert_urls_to_strings(data)
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
        data = self._convert_urls_to_strings(data)
        result = self.changes.insert_one(data)
        return str(result.inserted_id)

    def get_changes(self, competitor_id: str) -> List[dict]:
        print(f"DEBUG: Getting changes for competitor_id: {competitor_id}")
        docs = list(self.changes.find({"competitor_id": competitor_id}))
        print(f"DEBUG: Found {len(docs)} changes for competitor_id: {competitor_id}")
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs
    
    def get_all_changes(self) -> List[dict]:
        """Get all changes from all competitors"""
        print(f"DEBUG: Getting all changes from collection: {self.changes.name}")
        docs = list(self.changes.find({}))
        print(f"DEBUG: Found {len(docs)} documents in changes collection")
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Announcements
    # ----------------------------
    def add_announcement(self, announcement: Announcement) -> str:
        data = announcement.model_dump()
        data = self._convert_urls_to_strings(data)
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
        data = self._convert_urls_to_strings(data)
        result = self.reports.insert_one(data)
        return str(result.inserted_id)

    def get_reports(self) -> List[dict]:
        docs = list(self.reports.find({}))
        for d in docs:
            d["id"] = str(d["_id"])
            del d["_id"]
        return docs

    # ----------------------------
    # Delete operations
    # ----------------------------
    def delete_competitor(self, competitor_id: str) -> dict:
        """Delete a competitor and all related data by competitor_id"""
        result_comp = self.competitors.delete_one({"_id": ObjectId(competitor_id)})
        result_snaps = self.snapshots.delete_many({"competitor_id": competitor_id})
        result_changes = self.changes.delete_many({"competitor_id": competitor_id})
        result_ann = self.announcements.delete_many({"competitor_id": competitor_id})
        return {
            "deleted_competitors": result_comp.deleted_count,
            "deleted_snapshots": result_snaps.deleted_count,
            "deleted_changes": result_changes.deleted_count,
            "deleted_announcements": result_ann.deleted_count,
        }