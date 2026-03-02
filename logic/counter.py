from pymongo import MongoClient
from datetime import datetime
from zoneinfo import ZoneInfo
import certifi
import math
import threading
import queue

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

        # Async write queues so DB latency does not freeze the video loop.
        self._event_queue: "queue.Queue[dict]" = queue.Queue()
        self._stop_queue: "queue.Queue[dict]" = queue.Queue()
        self._db_thread_running = True

        self._db_thread = threading.Thread(
            target=self._db_worker,
            name="MongoWriter",
            daemon=True,
        )
        self._db_thread.start()

        print("✅ MongoDB Atlas connected (async writes enabled)")

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

        # Enqueue individual event for async write to MongoDB so
        # the video processing loop never blocks on network latency.
        self._event_queue.put({
            "track_id": track_id,
            "direction": direction,
            "stop": stop,
            "stop_index": stop_index,
            "timestamp": timestamp,
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

        # Enqueue stop summary for async write so we do not block
        # the main loop at stop transitions.
        self._stop_queue.put({
            "stop": stop,
            "stop_index": stop_index,
            "entered": self.entered,
            "exited": self.exited,
            "inside": self.inside,
            "timestamp": timestamp,
        })

    # Get current counts
    def get_counts(self):
        
        # Returns (entered, exited, inside)
        
        return self.entered, self.exited, self.inside

    def _db_worker(self):
        """
        Background worker that flushes queued events and stop summaries
        to MongoDB. Runs as a daemon so UI / video loop never blocks.
        """
        while self._db_thread_running or not self._queues_empty():
            try:
                # Prioritize event writes; fall back to stop docs.
                try:
                    event = self._event_queue.get(timeout=0.1)
                    try:
                        self.events.insert_one(event)
                    except Exception as e:
                        print(f"[MongoDB] Failed to write event: {e}")
                    finally:
                        self._event_queue.task_done()
                    continue
                except queue.Empty:
                    pass

                try:
                    stop_doc = self._stop_queue.get_nowait()
                    try:
                        self.stops.insert_one(stop_doc)
                    except Exception as e:
                        print(f"[MongoDB] Failed to write stop summary: {e}")
                    finally:
                        self._stop_queue.task_done()
                except queue.Empty:
                    pass
            except Exception as e:
                # Last-resort catch so background thread never dies silently.
                print(f"[MongoDB] DB worker error: {e}")

    def _queues_empty(self) -> bool:
        return self._event_queue.empty() and self._stop_queue.empty()

    def close(self):
        """
        Signal the background DB writer to stop after flushing queues
        and close the MongoDB client. Call this once on clean shutdown.
        """
        # Stop accepting new work and wait for queues to drain.
        self._db_thread_running = False
        try:
            self._event_queue.join()
            self._stop_queue.join()
        except Exception:
            pass
        # Now it is safe to close the client; worker loop will exit.
        self.client.close()
