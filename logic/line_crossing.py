import cv2

class LineCrossing:
    ZONE_ABOVE = "above"
    ZONE_BELOW = "below"

    def __init__(
        self,
        line_position_ratio=0.38,
        hysteresis_ratio=0.02,
        cooldown_frames=45,
        invert_direction=False,
    ):
        
        self.previous_positions = {}   
        self.previous_zone = {}       
        self.cooldown_until = {}     
        self.line_ratio = line_position_ratio
        self.hysteresis_ratio = hysteresis_ratio
        self.cooldown_frames = cooldown_frames
        self.invert_direction = invert_direction
        self._frame_index = 0

    def _get_zone(self, centroid_y, line_y, frame_height):
        margin = int(frame_height * self.hysteresis_ratio)
        if centroid_y < line_y - margin:
            return self.ZONE_ABOVE
        if centroid_y > line_y + margin:
            return self.ZONE_BELOW
        return None 

    def check_crossing(self, track_id, centroid_y, frame_height):
       
        line_y = int(frame_height * self.line_ratio)
        current_zone = self._get_zone(centroid_y, line_y, frame_height)

        if track_id in self.cooldown_until:
            if self._frame_index <= self.cooldown_until[track_id]:
                self.previous_positions[track_id] = centroid_y
                if current_zone is not None:
                    self.previous_zone[track_id] = current_zone
                return None
            else:
                del self.cooldown_until[track_id]

        if track_id not in self.previous_positions:
            self.previous_positions[track_id] = centroid_y
            if current_zone is not None:
                self.previous_zone[track_id] = current_zone
            return None

        prev_y = self.previous_positions[track_id]
        prev_zone = self.previous_zone.get(track_id)
        self.previous_positions[track_id] = centroid_y
        if current_zone is not None:
            self.previous_zone[track_id] = current_zone

        if prev_zone == self.ZONE_ABOVE and current_zone == self.ZONE_BELOW:
            self.cooldown_until[track_id] = self._frame_index + self.cooldown_frames
            return "OUT" if self.invert_direction else "IN"
        if prev_zone == self.ZONE_BELOW and current_zone == self.ZONE_ABOVE:
            self.cooldown_until[track_id] = self._frame_index + self.cooldown_frames
            return "IN" if self.invert_direction else "OUT"

        return None

    def tick(self):
        self._frame_index += 1

    def draw_line(self, frame):
        h, w, _ = frame.shape
        line_y = int(h * self.line_ratio)
        margin = int(h * self.hysteresis_ratio)
        cv2.line(frame, (0, line_y), (w, line_y), (0, 255, 255), 2)
        cv2.line(frame, (0, line_y - margin), (w, line_y - margin), (0, 200, 200), 1)
        cv2.line(frame, (0, line_y + margin), (w, line_y + margin), (0, 200, 200), 1)
        cv2.putText(
            frame,
            "ENTRY / EXIT LINE",
            (20, line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )
