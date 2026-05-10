"""
ViBe Background Subtraction Algorithm
======================================
Implementation based on the original paper:
"ViBe: A Universal Background Subtraction Algorithm for Video Sequences"
by Olivier Barnich and Marc Van Droogenbroeck (2011).

Key features:
- Single-frame initialization using spatial neighborhood sampling
- Random sample replacement for model update
- Spatial propagation to neighboring pixels
- Fully vectorized NumPy implementation for real-time performance
"""

import numpy as np


class ViBe:
    """
    ViBe (Visual Background Extractor) background subtraction algorithm.
    
    Parameters
    ----------
    num_samples : int
        Number of samples stored per pixel in the background model (N).
        Default: 20
    match_radius : int
        Radius threshold for pixel matching (R). A pixel value is considered
        matching a sample if |pixel - sample| < R.
        Default: 20
    min_matches : int
        Minimum number of matching samples required to classify a pixel
        as background (#min).
        Default: 2
    update_factor : int
        Subsampling factor for random update (phi). A background pixel
        has a 1/phi chance of updating its model each frame.
        Default: 16
    """

    def __init__(self, num_samples=20, match_radius=20, min_matches=2, update_factor=16):
        self.N = num_samples          # Number of samples per pixel
        self.R = match_radius         # Matching radius threshold
        self.min_matches = min_matches  # Minimum matches for background
        self.phi = update_factor      # Subsampling factor (1/phi update chance)
        
        # Background model: will be shape (H, W, N) after initialization
        self.samples = None
        self.height = 0
        self.width = 0
        self._initialized = False

    def initialize(self, first_frame):
        """
        Initialize the background model from a single frame.
        
        For each pixel, N samples are randomly selected from its 3x3 spatial
        neighborhood. This allows the algorithm to start classifying from
        the very next frame.
        
        Parameters
        ----------
        first_frame : np.ndarray
            First frame of the video (grayscale, shape HxW).
        """
        # Ensure grayscale
        if len(first_frame.shape) == 3:
            frame = np.mean(first_frame, axis=2).astype(np.uint8)
        else:
            frame = first_frame.copy()

        self.height, self.width = frame.shape
        
        # Initialize sample storage: (H, W, N) array
        self.samples = np.zeros(
            (self.height, self.width, self.N), dtype=np.uint8
        )

        # Pad the frame to handle border pixels (reflect padding)
        padded = np.pad(frame, 1, mode='reflect')

        # For each sample slot, pick a random neighbor from the 3x3 neighborhood
        for i in range(self.N):
            # Generate random offsets in range [-1, 0, 1] for rows and columns
            row_offsets = np.random.randint(-1, 2, size=(self.height, self.width))
            col_offsets = np.random.randint(-1, 2, size=(self.height, self.width))

            # Create coordinate grids
            rows = np.arange(self.height).reshape(-1, 1) + 1  # +1 for padding offset
            cols = np.arange(self.width).reshape(1, -1) + 1

            # Apply random offsets to get neighbor coordinates
            sample_rows = rows + row_offsets
            sample_cols = cols + col_offsets

            # Sample from padded frame using the random neighbor coordinates
            self.samples[:, :, i] = padded[sample_rows, sample_cols]

        self._initialized = True

    def _segment(self, frame):
        """
        Classify each pixel as foreground or background.
        
        A pixel is background if at least min_matches of its N stored
        samples fall within radius R of the current pixel value.
        
        Parameters
        ----------
        frame : np.ndarray
            Current frame (grayscale, HxW).
            
        Returns
        -------
        fg_mask : np.ndarray
            Foreground mask (255 = foreground, 0 = background).
        """
        # Compute absolute difference between current frame and all samples
        # frame shape: (H, W) -> expand to (H, W, 1) for broadcasting
        frame_expanded = frame[:, :, np.newaxis].astype(np.int16)
        samples_int = self.samples.astype(np.int16)
        
        # Count matches: |pixel - sample| < R
        distances = np.abs(frame_expanded - samples_int)
        matches = np.sum(distances < self.R, axis=2)

        # Background if matches >= min_matches
        fg_mask = np.where(matches >= self.min_matches, 0, 255).astype(np.uint8)
        
        return fg_mask

    def _update(self, frame, fg_mask):
        """
        Update the background model using random subsampling.
        
        For each background pixel:
        1. With probability 1/phi, replace a random sample with current value
        2. With probability 1/phi, also update a random neighbor's model
        
        Parameters
        ----------
        frame : np.ndarray
            Current frame (grayscale, HxW).
        fg_mask : np.ndarray
            Foreground mask from segmentation step.
        """
        # Create boolean mask for background pixels
        bg_mask = (fg_mask == 0)

        # --- Self-update: randomly update own model ---
        # Generate random numbers to decide which pixels to update (1/phi chance)
        update_chance = np.random.randint(0, self.phi, size=(self.height, self.width))
        pixels_to_update = bg_mask & (update_chance == 0)

        if np.any(pixels_to_update):
            # Choose a random sample index to replace
            random_indices = np.random.randint(0, self.N, size=(self.height, self.width))
            
            # Get coordinates of pixels to update
            update_rows, update_cols = np.where(pixels_to_update)
            sample_indices = random_indices[update_rows, update_cols]
            
            # Replace chosen sample with current pixel value
            self.samples[update_rows, update_cols, sample_indices] = frame[update_rows, update_cols]

        # --- Spatial propagation: update a random neighbor's model ---
        propagate_chance = np.random.randint(0, self.phi, size=(self.height, self.width))
        pixels_to_propagate = bg_mask & (propagate_chance == 0)

        if np.any(pixels_to_propagate):
            prop_rows, prop_cols = np.where(pixels_to_propagate)

            # Generate random neighbor offsets
            row_offsets = np.random.randint(-1, 2, size=len(prop_rows))
            col_offsets = np.random.randint(-1, 2, size=len(prop_rows))

            # Compute neighbor coordinates with boundary clamping
            neighbor_rows = np.clip(prop_rows + row_offsets, 0, self.height - 1)
            neighbor_cols = np.clip(prop_cols + col_offsets, 0, self.width - 1)

            # Choose random sample index in neighbor's model
            random_indices = np.random.randint(0, self.N, size=len(prop_rows))

            # Propagate current pixel value to neighbor's model
            self.samples[neighbor_rows, neighbor_cols, random_indices] = frame[prop_rows, prop_cols]

    def apply(self, frame):
        """
        Process a single frame through the ViBe algorithm.
        
        Performs segmentation and model update in one step.
        
        Parameters
        ----------
        frame : np.ndarray
            Input frame (grayscale or BGR).
            
        Returns
        -------
        fg_mask : np.ndarray
            Binary foreground mask (255 = foreground, 0 = background).
        """
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = np.mean(frame, axis=2).astype(np.uint8)
        else:
            gray = frame.copy()

        # Initialize on first frame
        if not self._initialized:
            self.initialize(gray)
            # Return empty mask for first frame (no detection possible)
            return np.zeros((self.height, self.width), dtype=np.uint8)

        # Ensure frame dimensions match the model
        if gray.shape != (self.height, self.width):
            raise ValueError(
                f"Frame size {gray.shape} doesn't match model size "
                f"({self.height}, {self.width})"
            )

        # Step 1: Segment (classify foreground/background)
        fg_mask = self._segment(gray)

        # Step 2: Update background model
        self._update(gray, fg_mask)

        return fg_mask

    @property
    def is_initialized(self):
        """Check if the background model has been initialized."""
        return self._initialized

    def get_background_image(self):
        """
        Generate an approximate background image from the model.
        
        Returns the median of all stored samples for each pixel.
        
        Returns
        -------
        bg_image : np.ndarray
            Estimated background image (grayscale).
        """
        if not self._initialized:
            return None
        return np.median(self.samples, axis=2).astype(np.uint8)

    def reset(self):
        """Reset the background model."""
        self.samples = None
        self._initialized = False
        self.height = 0
        self.width = 0
