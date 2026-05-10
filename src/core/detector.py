"""
Moving Object Detector
======================
Post-processes ViBe foreground masks to detect individual moving objects.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Detection:
    """Represents a single detected moving object."""
    bbox: Tuple[int, int, int, int]
    centroid: Tuple[int, int]
    area: float
    contour: np.ndarray = field(repr=False)


class ObjectDetector:
    """Detects moving objects from a ViBe foreground mask."""

    def __init__(self, min_area=500, max_area=100000,
                 erosion_kernel=3, erosion_iterations=1,
                 dilation_kernel=5, dilation_iterations=2,
                 closing_kernel=7):
        self.min_area = min_area
        self.max_area = max_area
        self.erosion_kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_kernel, erosion_kernel))
        self.dilation_kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_kernel, dilation_kernel))
        self.closing_kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (closing_kernel, closing_kernel))
        self.erosion_iterations = erosion_iterations
        self.dilation_iterations = dilation_iterations

    def clean_mask(self, fg_mask):
        """Apply morphological operations: erosion -> dilation -> closing."""
        cleaned = cv2.erode(fg_mask, self.erosion_kern, iterations=self.erosion_iterations)
        cleaned = cv2.dilate(cleaned, self.dilation_kern, iterations=self.dilation_iterations)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, self.closing_kern)
        return cleaned

    def detect(self, fg_mask):
        """Full detection pipeline. Returns (detections, cleaned_mask)."""
        cleaned = self.clean_mask(fg_mask)
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w // 2, y + h // 2
                detections.append(Detection(bbox=(x, y, w, h), centroid=(cx, cy), area=area, contour=contour))
        
        return detections, cleaned

    def get_contour_features(self, contour):
        """Extract shape descriptors from a contour."""
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        extent = float(area) / (w * h) if (w * h) > 0 else 0
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        return {'area': area, 'perimeter': perimeter, 'aspect_ratio': aspect_ratio, 'extent': extent, 'solidity': solidity}
