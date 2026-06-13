#!/usr/bin/env python
"""
Model Evaluation Script
"""

import argparse
import time
from pathlib import Path

import torch
import numpy as np
from ultralytics import YOLO


def evaluate(
    model_path: str = "models/best_icon_detector.pt",
    data_yaml: str = "data/data.yaml",
    split: str = "test"
):
    """
    Evaluate model performance.
    
    Args:
        model_path: Path to model weights
        data_yaml: Path to dataset config
        split: Dataset split to evaluate
    """
    model = YOLO(model_path)
    
    results = model.val(
        data=data_yaml,
        split=split,
        imgsz=640,
        device=0 if torch.cuda.is_available() else "cpu",
        plots=True
    )
    
    print("\n" + "=" * 50)
    print("Evaluation Results")
    print("=" * 50)
    print(f"mAP50:     {results.box.map50:.4f}")
    print(f"mAP50-95:  {results.box.map:.4f}")
    print(f"Precision: {results.box.mp:.4f}")
    print(f"Recall:    {results.box.mr:.4f}")
    print("=" * 50)
    
    return results


def benchmark(
    model_path: str = "models/best_icon_detector.pt",
    images_dir: str = "data/processed/test/images",
    num_samples: int = 100
):
    """
    Benchmark inference speed.
    
    Args:
        model_path: Path to model weights
        images_dir: Directory with test images
        num_samples: Number of images to test
    """
    model = YOLO(model_path)
    
    images = list(Path(images_dir).glob("*.jpg"))[:num_samples]
    if not images:
        images = list(Path(images_dir).glob("*.png"))[:num_samples]
    
    if not images:
        print(f"No images found in {images_dir}")
        return
    
    # Warmup
    for _ in range(5):
        model.predict(str(images[0]), verbose=False)
    
    # Benchmark
    times = []
    for img in images:
        start = time.time()
        model.predict(str(img), verbose=False)
        times.append((time.time() - start) * 1000)
    
    print("\n" + "=" * 50)
    print("Inference Speed")
    print("=" * 50)
    print(f"Mean:   {np.mean(times):.2f} ms")
    print(f"Median: {np.median(times):.2f} ms")
    print(f"Min:    {np.min(times):.2f} ms")
    print(f"Max:    {np.max(times):.2f} ms")
    print(f"FPS:    {1000 / np.mean(times):.1f}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Evaluate icon detector")
    parser.add_argument("--model", default="models/best_icon_detector.pt")
    parser.add_argument("--data", default="data/data.yaml")
    parser.add_argument("--benchmark", action="store_true", help="Run speed benchmark")
    parser.add_argument("--images", default="data/processed/test/images")
    
    args = parser.parse_args()
    
    if args.benchmark:
        benchmark(args.model, args.images)
    else:
        evaluate(args.model, args.data)


if __name__ == "__main__":
    main()
