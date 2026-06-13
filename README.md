# Multi-Modal Icon Vision System

Advanced Deep Learning for Mobile UI Understanding using YOLOv11, OmniParser, and OCR Integration.

## Features

- **YOLOv11 Icon Detection**: Fast and accurate mobile UI icon detection
- **OmniParser Integration**: Advanced multi-modal UI element parsing
- **Supervision Library**: Enhanced visualization and tracking capabilities
- **Multi-Modal OCR**: Text extraction with EasyOCR and Tesseract
- **Icon-Text Correlation**: Semantic relationship mapping
- **REST API**: Production-ready Flask API
- **Real-time Analysis**: 333 FPS inference on RTX 4090

## Performance

| Metric    | Value                       |
| --------- | --------------------------- |
| mAP50     | 43.5%                       |
| mAP50-95  | 28.4%                       |
| Inference | 3.0ms (333 FPS on RTX 4090) |
| Classes   | 26                          |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: For advanced UI parsing
pip install omniglyph

# Optional: For enhanced visualization
pip install supervision
```

## Requirements

- **Core**: PyTorch 2.5+, Ultralytics 8.3+
- **Multi-Modal**: OmniParser (omniglyph), EasyOCR, Tesseract
- **Visualization**: Supervision, OpenCV, Matplotlib
- **Web**: Flask 3.1+
- **GPU Support**: CUDA 12.1+ (optional, CPU fallback supported)

## Usage

### Start Server

```bash
python run.py serve
```

### Advanced Multi-Modal Analysis

```python
from src.core.analyzer import MultiModalAnalyzer
import cv2

# Initialize with OmniParser support
analyzer = MultiModalAnalyzer(
    model_path="models/best_icon_detector.pt",
    enable_omniparser=True
)

# Analyze image
image = cv2.imread("screenshot.png")
results = analyzer.analyze(
    image,
    enable_ocr=True,
    enable_advanced_parsing=True
)

# Results include:
# - icons: Detected icon classes and positions
# - texts: Extracted text regions
# - pairs: Icon-text semantic correlations
# - advanced_elements: UI elements from OmniParser
```

### Enhanced Visualization with Supervision

```python
from src.core.detector import IconDetector
import cv2

detector = IconDetector("models/best_icon_detector.pt")
image = cv2.imread("screenshot.png")

# Detect icons
detections = detector.detect(image)

# Visualize with enhanced annotations
annotated = detector.visualize(image, detections)
cv2.imwrite("output.png", annotated)
```

### Train Model

```bash
python train.py --epochs 100
```

### Evaluate Model

```bash
python evaluate.py --model models/best_icon_detector.pt
```

## Project Structure

```
├── src/
│   ├── core/           # Detection & analysis
│   │   ├── detector.py # YOLOv11 icon detector
│   │   ├── ocr.py      # EasyOCR engine
│   │   └── analyzer.py # Multi-modal analyzer
│   ├── api/            # REST API
│   │   └── app.py      # Flask application
│   └── utils/          # Utilities
│       ├── config.py   # Configuration
│       └── visualization.py
├── frontend/           # Web interface
├── config/             # Configuration files
├── models/             # Model weights
├── data/               # Dataset
├── tests/              # Unit tests
├── run.py              # Main entry point
├── train.py            # Training script
└── evaluate.py         # Evaluation script
```

## API Endpoints

| Endpoint   | Method | Description             |
| ---------- | ------ | ----------------------- |
| `/health`  | GET    | Health check            |
| `/predict` | POST   | Icon detection          |
| `/analyze` | POST   | Multi-modal analysis    |
| `/explain` | POST   | Prediction explanations |
| `/classes` | GET    | List icon classes       |

## Docker

```bash
docker build -t icon-vision .
docker run -p 5000:5000 icon-vision
```

## Team

- Harshit Sharma
- Sushant Thakur
- Kamal

**Supervisor:** Dr. Surjit Singh  
**Institution:** Thapar Institute of Engineering & Technology, Patiala
