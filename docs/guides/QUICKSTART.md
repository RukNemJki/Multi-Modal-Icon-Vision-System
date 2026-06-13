# 🚀 Quick Start Guide - Multi-Modal Icon Vision System

## Get Started in 5 Minutes!

### Step 1: Install Dependencies (2 min)

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Run Tests (1 min)

```powershell
# Verify installation
python tests/test_all.py
```

### Step 3: Start the Demo (2 min)

```powershell
# Start the backend server
cd backend
python app.py
```

In a new terminal:
```powershell
# Serve the frontend
cd frontend
python -m http.server 8000
```

### Step 4: Open in Browser

Visit: `http://localhost:8000`

---

## What You Can Do Now

### ✅ Demo Mode (No Training Required)

The system automatically downloads a pretrained YOLOv8 model on first run. You can:

1. Upload any mobile screenshot
2. See general object detection in action
3. Test the web interface
4. Explore the API endpoints

### 🎓 Full Training Pipeline

To train your own icon detection model:

#### 1. Get the Rico Dataset

Download from: https://interactionmining.org/rico

Place files in:
```
data/raw/
├── rico_screenshots/    # Screenshot images
└── rico_annotations/    # JSON annotations
```

#### 2. Process Dataset

```powershell
python scripts/dataset_processor.py
```

This creates:
- `data/processed/train/` - Training images & labels
- `data/processed/val/` - Validation images & labels  
- `data/processed/test/` - Test images & labels
- `data/data.yaml` - YOLO configuration

#### 3. Train Model

```powershell
python scripts/train_model.py
```

Monitor training:
```powershell
tensorboard --logdir runs/train
```

Training takes 2-6 hours on GPU (NVIDIA RTX 3070 or better recommended).

#### 4. Evaluate Model

```powershell
python scripts/evaluate_model.py
```

Results saved to `evaluation/`

#### 5. Use Your Trained Model

The backend automatically loads `models/best_icon_detector.pt` if it exists!

---

## Common Issues & Solutions

### Issue: "No module named 'torch'"

**Solution:**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "CUDA out of memory"

**Solution:** Reduce batch size in `config/config.yaml`:
```yaml
training:
  batch_size: 8  # Reduce from 16
```

### Issue: "API not responding"

**Solution:** Check if port 5000 is in use:
```powershell
# Use different port
$env:FLASK_RUN_PORT="5001"
python backend/app.py
```

Update `frontend/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:5001';
```

### Issue: "Frontend not loading"

**Solution:** Try a different port:
```powershell
cd frontend
python -m http.server 8080
```

---

## Project Milestones

### ✅ Phase 1: Mid-Semester (Current)
- [x] Project structure
- [x] Dataset processing scripts  
- [x] YOLOv8 training pipeline
- [x] Flask backend API
- [x] Web frontend interface
- [x] Evaluation tools
- [x] Documentation

### 🔜 Phase 2: Final Semester (Sep-Nov 2025)
- [ ] OCR integration
- [ ] Multi-modal late fusion
- [ ] Semantic label generation
- [ ] Mobile app deployment
- [ ] Performance optimization
- [ ] Research paper submission

---

## Directory Overview

```
capstone/
├── 📁 backend/          → Flask API server
├── 📁 frontend/         → Web interface  
├── 📁 scripts/          → Training & processing scripts
├── 📁 config/           → Configuration files
├── 📁 data/             → Datasets (add your data here)
├── 📁 models/           → Trained model weights
├── 📁 logs/             → Training logs
├── 📁 runs/             → Experiment runs
├── 📁 evaluation/       → Evaluation results
├── 📁 tests/            → Unit tests
└── 📄 README.md         → Full documentation
```

---

## Next Steps

1. **Explore the code**: Start with `backend/app.py` and `scripts/train_model.py`
2. **Read the paper**: Check `ghfhf.pdf` for theoretical background
3. **Customize config**: Edit `config/config.yaml` for your needs
4. **Train on your data**: Follow the full pipeline above
5. **Deploy**: Use ONNX export for production deployment

---

## Getting Help

- 📖 Full docs: See `README.md`
- 🐛 Issues: Check `tests/test_all.py` for diagnostics
- 💬 Questions: Contact project team

---

**Happy Icon Detecting! 🎯**

Made with ❤️ by Harshit, Sushant, and Kamal  
TIET Patiala • 2025
