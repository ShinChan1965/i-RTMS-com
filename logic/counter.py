from pymongo import MongoClient
from datetime import datetime
from zoneinfo import ZoneInfo
import certifi
import math

from config.config import MONGO_URI

CROSSING_DEDUP_RADIUS_PX = 120
CROSSING_DEDUP_SECONDS = 1.5
MAX_RECENT_CROSSINGS = 50


class PassengerCounter:
    def __init__(self):
        # Counters
        self.entered = 0
        self.exited = 0
        self.inside = 0

        # Prevent duplicate counting per stop (track_id, stop_index)
        self.processed_ids = set()
        # Recent crossings (cx, cy, direction, timestamp) for spatial dedup on ID switch
        self.recent_crossings = []

        # Timezone (India)
        self.tz = ZoneInfo("Asia/Kolkata")

        # MongoDB Atlas connection
        self.client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where()
        )

        self.db = self.client["iRTMS"]
        self.events = self.db["passenger_events"]
        self.stops = self.db["stop_counts"]

        print("✅ MongoDB Atlas connected")

    # Update count when line is crossed
    def update(self, track_id, direction, stop, stop_index, centroid_x=None, centroid_y=None):

        key = (track_id, stop_index)
        if key in self.processed_ids:
            return

        # Spatial-temporal dedup: same person with new ID crossing again
        if centroid_x is not None and centroid_y is not None:
            now = datetime.now(self.tz)
            self._prune_recent_crossings(now)
            if self._is_duplicate_crossing(centroid_x, centroid_y, direction, now):
                return

        self.processed_ids.add(key)

        if direction == "IN":
            self.entered += 1
            self.inside += 1
        elif direction == "OUT":
            self.exited += 1
            self.inside = max(0, self.inside - 1)
        else:
            return

        timestamp = datetime.now(self.tz)
        if centroid_x is not None and centroid_y is not None:
            self.recent_crossings.append((centroid_x, centroid_y, direction, timestamp))
            if len(self.recent_crossings) > MAX_RECENT_CROSSINGS:
                self.recent_crossings.pop(0)

        # Store individual event
        self.events.insert_one({
            "track_id": track_id,
            "direction": direction,
            "stop": stop,
            "stop_index": stop_index,
            "timestamp": timestamp
        })

    def _prune_recent_crossings(self, now):
        # Remove crossings older than CROSSING_DEDUP_SECONDS.
        cutoff = now.timestamp() - CROSSING_DEDUP_SECONDS
        self.recent_crossings = [
            c for c in self.recent_crossings
            if c[3].timestamp() > cutoff
        ]

    def _is_duplicate_crossing(self, cx, cy, direction, now):
        # True if a recent crossing with same direction exists within radius.
        now_ts = now.timestamp()
        for (rcx, rcy, rdir, rts) in self.recent_crossings:
            if rdir != direction:
                continue
            if now_ts - rts.timestamp() > CROSSING_DEDUP_SECONDS:
                continue
            dist = math.hypot(cx - rcx, cy - rcy)
            if dist <= CROSSING_DEDUP_RADIUS_PX:
                return True
        return False

    # Store stop-wise summary
    def store_stop_data(self, stop, stop_index):
        
        # Stores aggregated passenger data for a stop.
        

        timestamp = datetime.now(self.tz)

        self.stops.insert_one({
            "stop": stop,
            "stop_index": stop_index,
            "entered": self.entered,
            "exited": self.exited,
            "inside": self.inside,
            "timestamp": timestamp
        })

    # Get current counts
    def get_counts(self):
        
        # Returns (entered, exited, inside)
        
        return self.entered, self.exited, self.inside
