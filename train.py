#!/usr/bin/env python
"""
YOLOv11 Model Training Script
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime

import torch
import yaml
from ultralytics import YOLO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_device():
    """Configure optimal device settings"""
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        logger.info(f"CUDA: {torch.cuda.get_device_name(0)}")
        return 0
    return "cpu"


def train(
    data_yaml: str = "data/data.yaml",
    model_name: str = "yolo11n",
    epochs: int = 100,
    batch_size: int = 16,
    imgsz: int = 640,
    resume: bool = False
):
    """
    Train YOLOv11 model.
    
    Args:
        data_yaml: Path to dataset configuration
        model_name: Model variant (yolo11n, yolo11s, etc.)
        epochs: Number of training epochs
        batch_size: Batch size
        imgsz: Input image size
        resume: Resume from last checkpoint
    """
    device = setup_device()
    
    # Load model
    model = YOLO(f"{model_name}.pt")
    logger.info(f"Loaded {model_name}")
    
    # Training arguments
    run_name = f"icon_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        project="runs/train",
        name=run_name,
        
        # Optimizer
        optimizer="SGD",
        lr0=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        
        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        
        # Performance
        amp=True,
        cache="ram",
        workers=8,
        
        # Other
        resume=resume,
        verbose=True,
        seed=42
    )
    
    # Save best model
    best_path = Path(f"runs/train/{run_name}/weights/best.pt")
    if best_path.exists():
        dest = Path("models/best_icon_detector.pt")
        dest.parent.mkdir(exist_ok=True)
        import shutil
        shutil.copy(best_path, dest)
        logger.info(f"Best model saved to {dest}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv11 icon detector")
    parser.add_argument("--data", default="data/data.yaml", help="Dataset config")
    parser.add_argument("--model", default="yolo11n", help="Model variant")
    parser.add_argument("--epochs", type=int, default=100, help="Epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--resume", action="store_true", help="Resume training")
    
    args = parser.parse_args()
    
    train(
        data_yaml=args.data,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        resume=args.resume
    )


if __name__ == "__main__":
    main()
