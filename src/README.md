# Moving Object Detection and Trajectory Tracking

This project implements a `VIBE Background Extractor (NumPy)` pipeline for moving object detection and trajectory tracking using Python, OpenCV, and NumPy.

## Project Overview

- `main.py` contains the main pipeline and entry point.
- `vibe.py` implements the VIBE background subtraction algorithm.
- `tracker.py` implements the centroid-based object tracker.
- `utils.py` contains utility functions for video path resolution.
- The pipeline reads a video file, computes a binary foreground mask, filters contours, and tracks object centroids over time.
- The tracked objects are visualized with bounding boxes, IDs, and trajectory lines.

## Features

- ViBe background subtraction implementation
- Contour filtering for object detection
- Centroid-based tracker with object registration, disappearance handling, and trajectory visualization
- Real-time display of both detected objects and the segmentation mask

## Requirements

- Python 3.10
- `opencv-python` 4.13.0
- `numpy` 2.2.6

## Installation

1. Create and activate a Python virtual environment in the project folder:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Usage

Use the default Dataset video or pass a custom video path with `--video`.

```powershell
python main.py
python main.py --video Dataset\VIRAT_S_010204_05_000856_000890.mp4
```

The script opens two windows:

- `Frame` for the annotated tracked video
- `Mask` for the foreground segmentation output

Press `Esc` to exit.

## Notes

- The script now automatically uses the first `.mp4` file found in the `Dataset` folder when `--video` is omitted.
- If your dataset is stored elsewhere, pass the path with `python main.py --video <path>`.
- The implementation uses a fixed frame size of 480x270 and skips every other frame for speed.
- Before pushing to GitHub, do not include the local virtual environment folder `myenv/` or generated files such as `output.mp4`.

## License

This repository does not include an explicit license. Add one if you plan to publish or share the code.