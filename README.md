# Multi-Modal Icon Vision System

Deep Learning for Mobile UI Understanding using YOLOv11 and OCR Integration.

## Performance

| Metric | Value |
|--------|-------|
| mAP50 | 43.5% |
| mAP50-95 | 28.4% |
| Inference | 0.9ms (1111 FPS) |
| Classes | 26 |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start Server
```bash
python run.py serve
```

### Analyze Image
```bash
python run.py analyze path/to/image.png -o output.png
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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/predict` | POST | Icon detection |
| `/analyze` | POST | Multi-modal analysis |
| `/explain` | POST | Prediction explanations |
| `/classes` | GET | List icon classes |

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
