# 🎯 Moving Object Detection & Trajectory Tracking

A computer vision project that detects and tracks moving objects in video using a custom implementation of the **ViBe background subtraction algorithm** and a **centroid-based tracking system**.

---

## 📌 Overview

This project demonstrates a complete pipeline for **foreground segmentation, object detection, and trajectory tracking** using classical computer vision techniques.

The system processes video frames to:

* Separate moving objects from the background
* Detect valid object regions using contour filtering
* Track object movement across frames
* Visualize trajectories and object identities in real time

---

## ⚙️ Key Features

* 🧠 **ViBe Background Subtraction (NumPy Implementation)**
  Efficient pixel-level modeling for foreground detection.

* 🎯 **Contour-Based Object Detection**
  Filters noise using area, size, and aspect ratio constraints.

* 📍 **Centroid Tracking Algorithm**

  * Object ID assignment
  * Distance-based matching
  * Disappearance handling

* 📈 **Trajectory Visualization**
  Tracks and displays movement paths over time.

* ⚡ **Optimized for Performance**

  * Frame resizing (480×270)
  * Frame skipping for real-time processing

---

## 🏗️ Project Structure

```
IPCV_Project/
│── main.py              # Main pipeline (ViBe + tracking)
│── Dataset/             # Input video files
│── requirements.txt     # Dependencies
│── README.md
```

---

## 🧰 Tech Stack

* **Language:** Python 3.10
* **Libraries:**

  * OpenCV (`opencv-python`)
  * NumPy

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/moving-object-detection.git
cd moving-object-detection
```

2. Create a virtual environment:

```bash
python -m venv myenv
.\myenv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the program using:

```bash
python main.py
```

Or specify a custom video:

```bash
python main.py --video Dataset\your_video.mp4
```

---

## 🖥️ Output

The application opens two windows:

* **Frame** → Displays tracked objects with bounding boxes, IDs, and trajectories
* **Mask** → Shows foreground segmentation output

Press **ESC** to exit.

---

## 🧪 Implementation Details

* Uses **ViBe algorithm** for adaptive background modeling
* Applies **morphological operations** to clean segmentation masks
* Uses **Euclidean distance matching** for object tracking
* Maintains object trajectories using historical centroid data

---

## ⚠️ Limitations

* May struggle with:

  * Occlusion between objects
  * Complex lighting changes
  * Shadows and reflections

These are known limitations of classical computer vision approaches.

---

## 🚀 Future Improvements

* Integrate **YOLO-based object detection**
* Use **DeepSORT for robust tracking**
* Add **object counting and analytics**
* Improve robustness to lighting and shadows

---

## 👤 Author

**Deepak K**

---
