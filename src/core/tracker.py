"""
Multi-Object Trajectory Tracker
================================
Centroid-based tracker that assigns unique IDs to detected objects
and maintains trajectory path history for visualization.
"""

import numpy as np
from collections import OrderedDict, deque
from scipy.spatial.distance import cdist


class Track:
    """Represents a single tracked object with its trajectory history."""

    def __init__(self, track_id, centroid, max_history=60):
        self.id = track_id
        self.centroid = centroid
        self.path = deque(maxlen=max_history)
        self.path.append(centroid)
        self.lost_count = 0
        self.total_frames = 1
        self.bbox = None
        self.velocity = (0, 0)
        self.active = True

    def update(self, centroid, bbox=None):
        """Update track with new detection."""
        # Calculate velocity from last position
        if len(self.path) > 0:
            last = self.path[-1]
            self.velocity = (centroid[0] - last[0], centroid[1] - last[1])
        
        self.centroid = centroid
        self.path.append(centroid)
        self.bbox = bbox
        self.lost_count = 0
        self.total_frames += 1

    def mark_lost(self):
        """Mark this track as lost for one frame."""
        self.lost_count += 1

    def get_direction_angle(self):
        """Get motion direction in degrees (0=right, 90=down)."""
        if len(self.path) < 2:
            return 0
        dx, dy = self.velocity
        if dx == 0 and dy == 0:
            return 0
        return np.degrees(np.arctan2(dy, dx))

    def get_speed(self):
        """Get current speed in pixels/frame."""
        return np.sqrt(self.velocity[0]**2 + self.velocity[1]**2)


class CentroidTracker:
    """
    Multi-object tracker using centroid distance association.
    
    Parameters
    ----------
    max_lost : int
        Maximum frames an object can be lost before removal. Default: 30
    max_distance : float
        Maximum distance for centroid association. Default: 80
    max_history : int
        Maximum trajectory path points to store. Default: 60
    """

    def __init__(self, max_lost=30, max_distance=80, max_history=60):
        self.max_lost = max_lost
        self.max_distance = max_distance
        self.max_history = max_history
        self.tracks = OrderedDict()
        self._next_id = 1
        self.total_tracks_created = 0

    def update(self, detections):
        """
        Update tracks with new detections using greedy nearest-neighbor matching.
        
        Parameters
        ----------
        detections : list
            List of Detection objects from the detector.
            
        Returns
        -------
        tracks : dict
            Dictionary of active Track objects keyed by track ID.
        """
        # If no detections, mark all tracks as lost
        if len(detections) == 0:
            for track in list(self.tracks.values()):
                track.mark_lost()
                if track.lost_count > self.max_lost:
                    track.active = False
                    del self.tracks[track.id]
            return self.tracks

        # Extract centroids and bboxes from detections
        det_centroids = np.array([d.centroid for d in detections])
        det_bboxes = [d.bbox for d in detections]

        # If no existing tracks, create new ones for all detections
        if len(self.tracks) == 0:
            for i in range(len(detections)):
                self._create_track(det_centroids[i], det_bboxes[i])
            return self.tracks

        # Get existing track centroids
        track_ids = list(self.tracks.keys())
        track_centroids = np.array([self.tracks[tid].centroid for tid in track_ids])

        # Compute distance matrix between existing tracks and new detections
        dist_matrix = cdist(track_centroids, det_centroids)

        # Greedy matching: assign closest pairs first
        matched_tracks = set()
        matched_detections = set()

        # Sort all distances and match greedily
        rows, cols = np.unravel_index(np.argsort(dist_matrix, axis=None), dist_matrix.shape)
        
        for r, c in zip(rows, cols):
            if r in matched_tracks or c in matched_detections:
                continue
            if dist_matrix[r, c] > self.max_distance:
                continue
            
            # Match found: update the track
            tid = track_ids[r]
            self.tracks[tid].update(
                tuple(det_centroids[c].tolist()),
                det_bboxes[c]
            )
            matched_tracks.add(r)
            matched_detections.add(c)

        # Handle unmatched tracks (lost objects)
        for r in range(len(track_ids)):
            if r not in matched_tracks:
                tid = track_ids[r]
                self.tracks[tid].mark_lost()
                if self.tracks[tid].lost_count > self.max_lost:
                    self.tracks[tid].active = False
                    del self.tracks[tid]

        # Handle unmatched detections (new objects)
        for c in range(len(detections)):
            if c not in matched_detections:
                self._create_track(tuple(det_centroids[c].tolist()), det_bboxes[c])

        return self.tracks

    def _create_track(self, centroid, bbox=None):
        """Create a new track with a unique ID."""
        track = Track(self._next_id, centroid, self.max_history)
        track.bbox = bbox
        self.tracks[self._next_id] = track
        self._next_id += 1
        self.total_tracks_created += 1

    def get_active_count(self):
        """Return count of currently active tracks."""
        return len(self.tracks)

    def get_all_trajectories(self):
        """Return all trajectory paths for visualization."""
        trajectories = {}
        for tid, track in self.tracks.items():
            trajectories[tid] = list(track.path)
        return trajectories

    def reset(self):
        """Reset the tracker state."""
        self.tracks.clear()
        self._next_id = 1
        self.total_tracks_created = 0
