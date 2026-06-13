# Multi-Modal Icon Vision System

Deep learning pipeline for mobile UI understanding — combining YOLOv11 icon detection, OmniParser UI parsing, and dual-OCR text extraction into a unified REST API.

---

## Performance

| Metric | Value |
|---|---|
| mAP50 | 43.5% |
| mAP50-95 | 28.4% |
| Icon classes | 26 |
| Inference (RTX 3060–3080) | ~8–12ms per frame |
| Dataset size | 72k+ UI screenshots |
| API latency | <16ms (GPU), <80ms (CPU) |

> mAP50-95 is reported alongside mAP50 as it is the standard COCO benchmark metric and gives a more honest picture of localisation quality across IoU thresholds.

---

## What it does

Given a mobile UI screenshot, the system:

1. Detects and classifies icons across 26 categories using a fine-tuned YOLOv11 model (LYNX)
2. Extracts all text regions using EasyOCR and Tesseract in parallel
3. Parses structured UI elements (buttons, inputs, nav bars) using OmniParser
4. Fuses icon detections with nearby text via a late-fusion layer to produce semantic icon–text pairs
5. Returns structured JSON with bounding boxes, classes, confidence scores, and text associations

---

## Dataset

Training data consists of **72k+ UI screenshots** from two sources:

- **RICO dataset**: Large-scale public dataset of Android UI screenshots with hierarchy annotations
- **Self-collected captures**: Additional Android and web app screenshots captured manually to improve coverage of under-represented icon classes

Annotations were converted to YOLO format. Class distribution was imbalanced (common icons like "back", "menu", "search" dominate); addressed via class-weighted loss during training.

---

## Model

**Architecture**: YOLOv11n (nano variant) — chosen for inference speed over raw accuracy, suitable for real-time UI analysis pipelines.

**Training setup**:
- Framework: Ultralytics 8.3+, PyTorch 2.5+
- Hardware: RTX 3060/3070/3080
- Epochs: 100
- Input resolution: 640×640
- Augmentation: mosaic, random flip, HSV jitter

**Why 43.5% mAP50**: UI icon detection is a hard problem — icons are small (often <32×32px), visually similar across classes (e.g. "settings" vs "more options"), and lack the texture richness of natural images. 43.5% mAP50 / 28.4% mAP50-95 is competitive for a lightweight model on this domain.

---

## Multi-Modal Pipeline

```
Screenshot
    │
    ├─── YOLOv11 (LYNX) ──────────── icon bounding boxes + class labels
    │
    ├─── EasyOCR + Tesseract ──────── text regions + content
    │
    ├─── OmniParser ───────────────── structured UI elements
    │
    └─── Late-Fusion Layer ────────── icon–text semantic pairs + full UI map
```

**Late-fusion logic**: For each detected icon, the nearest text region (within a configurable pixel threshold) is associated using IoU-based proximity scoring. OmniParser results are merged as a secondary pass to catch elements the detector missed.

---

## Installation

```bash
git clone https://github.com/RukNemJki/Multi-Modal-Icon-Vision-System.git
cd Multi-Modal-Icon-Vision-System

pip install -r requirements.txt

# Optional: OmniParser integration
pip install omniglyph

# Optional: Enhanced visualisation
pip install supervision
```

**Requirements**: Python 3.8+, PyTorch 2.5+, Ultralytics 8.3+, Flask 3.1+, EasyOCR, OpenCV, CUDA 12.1+ (optional — CPU fallback supported)

---

## Usage

### Start API server

```bash
python run.py serve
```

### Run full multi-modal analysis

```python
from src.core.analyzer import MultiModalAnalyzer
import cv2

analyzer = MultiModalAnalyzer(
    model_path="models/best_icon_detector.pt",
    enable_omniparser=True
)

image = cv2.imread("screenshot.png")
results = analyzer.analyze(image, enable_ocr=True, enable_advanced_parsing=True)

# results keys:
# icons            — detected classes with bounding boxes and confidence
# texts            — OCR-extracted text regions
# pairs            — icon–text semantic associations
# advanced_elements — OmniParser structured UI elements
```

### Train from scratch

```bash
python train.py --epochs 100
```

### Evaluate

```bash
python evaluate.py --model models/best_icon_detector.pt
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/predict` | POST | Icon detection only |
| `/analyze` | POST | Full multi-modal analysis |
| `/explain` | POST | Per-detection explanation |
| `/classes` | GET | List all 26 icon classes |

---

## Docker

```bash
docker build -t icon-vision .
docker run -p 5000:5000 icon-vision
```

GPU passthrough (requires nvidia-container-toolkit):

```bash
docker run --gpus all -p 5000:5000 icon-vision
```

---

## Project Structure

```
├── src/
│   ├── core/
│   │   ├── detector.py       # YOLOv11 icon detector (LYNX)
│   │   ├── ocr.py            # EasyOCR + Tesseract engine
│   │   └── analyzer.py       # Multi-modal fusion pipeline
│   ├── api/
│   │   └── app.py            # Flask REST API
│   └── utils/
│       ├── config.py
│       └── visualization.py
├── frontend/                 # Web interface
├── config/                   # YAML configs
├── models/                   # Model weights
├── data/                     # Dataset (RICO + self-collected)
├── tests/
├── run.py                    # Entry point
├── train.py
└── evaluate.py
```

---

## Known Limitations

- **Small icon performance**: mAP50-95 of 28.4% reflects difficulty at strict IoU thresholds — small icons (<32px) are the primary failure case
- **Class imbalance**: Common icons (back, menu, search) are over-represented; rare classes have lower per-class AP
- **OCR on low-res screenshots**: Tesseract accuracy degrades below 72 DPI; EasyOCR is used as primary for low-resolution inputs
- **OmniParser dependency**: Optional — system degrades gracefully to YOLO + OCR only if `omniglyph` is not installed

---

## Team

- Harshit Sharma
- Sushant Thakur
- Kamal

**Supervisor**: Dr. Surjit Singh
**Institution**: Thapar Institute of Engineering & Technology, Patiala
**Year**: 2026
