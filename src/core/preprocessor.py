"""
Preprocessing Pipeline
======================
Applies a configurable sequence of image preprocessing operations
to improve the quality of moving object detection.

Pipeline stages:
1. Resize - Scale frames to a standard resolution
2. Denoise - Gaussian blur and/or median filter to reduce noise
3. Enhance - CLAHE contrast enhancement for better feature visibility
"""

import cv2
import numpy as np


class Preprocessor:
    """
    Configurable image preprocessing pipeline for video frames.
    
    Each preprocessing step can be independently enabled/disabled
    through the UI settings panel.
    
    Parameters
    ----------
    target_width : int
        Target width for frame resizing. Default: 640
    target_height : int
        Target height for frame resizing. Default: 480
    enable_resize : bool
        Enable frame resizing. Default: True
    enable_gaussian : bool
        Enable Gaussian blur denoising. Default: True
    enable_median : bool
        Enable median filter denoising. Default: False
    enable_clahe : bool
        Enable CLAHE contrast enhancement. Default: True
    gaussian_kernel : int
        Gaussian blur kernel size (must be odd). Default: 5
    gaussian_sigma : float
        Gaussian blur sigma value. Default: 1.0
    median_kernel : int
        Median filter kernel size (must be odd). Default: 5
    clahe_clip : float
        CLAHE clip limit. Default: 2.0
    clahe_grid : tuple
        CLAHE tile grid size. Default: (8, 8)
    """

    def __init__(self, target_width=640, target_height=480,
                 enable_resize=True, enable_gaussian=True,
                 enable_median=False, enable_clahe=True,
                 gaussian_kernel=5, gaussian_sigma=1.0,
                 median_kernel=5, clahe_clip=2.0, clahe_grid=(8, 8)):
        
        self.target_width = target_width
        self.target_height = target_height
        
        # Toggle switches for each preprocessing step
        self.enable_resize = enable_resize
        self.enable_gaussian = enable_gaussian
        self.enable_median = enable_median
        self.enable_clahe = enable_clahe
        
        # Parameters for each step
        self.gaussian_kernel = gaussian_kernel
        self.gaussian_sigma = gaussian_sigma
        self.median_kernel = median_kernel
        self.clahe_clip = clahe_clip
        self.clahe_grid = clahe_grid
        
        # Create CLAHE object (reusable)
        self._clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip,
            tileGridSize=self.clahe_grid
        )

    def resize(self, frame):
        """
        Resize frame to target dimensions while maintaining aspect ratio.
        
        Uses letterboxing (black padding) to fit the frame into the target
        size without distortion.
        
        Parameters
        ----------
        frame : np.ndarray
            Input frame (BGR or grayscale).
            
        Returns
        -------
        resized : np.ndarray
            Resized frame.
        """
        h, w = frame.shape[:2]
        
        # Calculate scaling factor to fit within target dimensions
        scale = min(self.target_width / w, self.target_height / h)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize with high-quality interpolation
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # If dimensions don't exactly match target, pad with black
        if new_w != self.target_width or new_h != self.target_height:
            if len(frame.shape) == 3:
                canvas = np.zeros((self.target_height, self.target_width, 3), dtype=np.uint8)
            else:
                canvas = np.zeros((self.target_height, self.target_width), dtype=np.uint8)
            
            # Center the resized frame on the canvas
            y_offset = (self.target_height - new_h) // 2
            x_offset = (self.target_width - new_w) // 2
            canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
            return canvas
        
        return resized

    def denoise_gaussian(self, frame):
        """
        Apply Gaussian blur for noise reduction.
        
        Gaussian blur is effective at removing high-frequency noise while
        preserving edge structure reasonably well.
        
        Parameters
        ----------
        frame : np.ndarray
            Input frame.
            
        Returns
        -------
        blurred : np.ndarray
            Denoised frame.
        """
        return cv2.GaussianBlur(
            frame,
            (self.gaussian_kernel, self.gaussian_kernel),
            self.gaussian_sigma
        )

    def denoise_median(self, frame):
        """
        Apply median filter for noise reduction.
        
        Median filter is particularly effective at removing salt-and-pepper
        noise while preserving edges better than Gaussian blur.
        
        Parameters
        ----------
        frame : np.ndarray
            Input frame.
            
        Returns
        -------
        filtered : np.ndarray
            Denoised frame.
        """
        return cv2.medianBlur(frame, self.median_kernel)

    def enhance_clahe(self, frame):
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        CLAHE improves local contrast, making it easier to detect objects
        in poorly lit or low-contrast regions of the frame.
        
        Parameters
        ----------
        frame : np.ndarray
            Input frame (BGR or grayscale).
            
        Returns
        -------
        enhanced : np.ndarray
            Contrast-enhanced frame.
        """
        if len(frame.shape) == 3:
            # Convert to LAB color space for better results
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            channels = list(cv2.split(lab))
            # Apply CLAHE only to the L (lightness) channel
            channels[0] = self._clahe.apply(channels[0])
            lab = cv2.merge(channels)
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale: apply directly
            return self._clahe.apply(frame)

    def process(self, frame):
        """
        Apply the full preprocessing pipeline to a frame.
        
        The pipeline applies enabled steps in order:
        1. Resize → 2. Gaussian Blur → 3. Median Filter → 4. CLAHE
        
        Parameters
        ----------
        frame : np.ndarray
            Raw input frame from video.
            
        Returns
        -------
        processed : np.ndarray
            Preprocessed frame ready for ViBe processing.
        """
        result = frame.copy()

        # Step 1: Resize
        if self.enable_resize:
            result = self.resize(result)

        # Step 2: Gaussian blur denoising
        if self.enable_gaussian:
            result = self.denoise_gaussian(result)

        # Step 3: Median filter denoising
        if self.enable_median:
            result = self.denoise_median(result)

        # Step 4: CLAHE enhancement
        if self.enable_clahe:
            result = self.enhance_clahe(result)

        return result

    def get_comparison(self, frame):
        """
        Generate a before/after comparison of preprocessing.
        
        Returns both the original and processed frames side by side
        for visualization purposes.
        
        Parameters
        ----------
        frame : np.ndarray
            Raw input frame.
            
        Returns
        -------
        comparison : np.ndarray
            Side-by-side comparison image.
        """
        processed = self.process(frame)
        
        # Resize original to match processed dimensions
        if self.enable_resize:
            original = self.resize(frame)
        else:
            original = frame.copy()
        
        # Create side-by-side comparison
        comparison = np.hstack([original, processed])
        
        # Add labels
        h = comparison.shape[0]
        cv2.putText(comparison, "Original", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(comparison, "Preprocessed", (original.shape[1] + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return comparison

    def update_clahe(self):
        """Recreate the CLAHE object after parameter changes."""
        self._clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip,
            tileGridSize=self.clahe_grid
        )
