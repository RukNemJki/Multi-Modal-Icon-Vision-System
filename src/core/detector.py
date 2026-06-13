"""
Icon Detector Module
YOLOv11-based icon detection for mobile UI screenshots
"""

import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Single icon detection result"""
    class_name: str
    class_id: int
    confidence: float
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": round(self.confidence, 4),
            "bbox": {
                "x1": round(self.bbox[0], 2),
                "y1": round(self.bbox[1], 2),
                "x2": round(self.bbox[2], 2),
                "y2": round(self.bbox[3], 2),
                "width": round(self.bbox[2] - self.bbox[0], 2),
                "height": round(self.bbox[3] - self.bbox[1], 2)
            }
        }


class IconDetector:
    """
    YOLOv11-based icon detector for mobile UI screenshots.
    
    Attributes:
        model: Loaded YOLO model
        class_names: List of icon class names
        device: Computing device (cuda/cpu)
    """
    
    # 26 icon classes as per report
    DEFAULT_CLASSES = [
        "back_button", "search_icon", "menu_icon", "home_icon",
        "settings_icon", "share_icon", "delete_icon", "edit_icon",
        "add_icon", "close_icon", "favorite_icon", "profile_icon",
        "notification_icon", "camera_icon", "gallery_icon", "download_icon",
        "upload_icon", "play_icon", "pause_icon", "refresh_icon",
        "filter_icon", "sort_icon", "calendar_icon", "location_icon",
        "phone_icon", "email_icon"
    ]
    
    def __init__(
        self,
        model_path: str = "models/best_icon_detector.pt",
        class_names: Optional[List[str]] = None,
        device: Optional[str] = None
    ):
        """
        Initialize icon detector.
        
        Args:
            model_path: Path to trained YOLO model weights
            class_names: Custom class names (uses defaults if None)
            device: Device to run inference on (auto-detect if None)
        """
        self.model_path = model_path
        self.class_names = class_names or self.DEFAULT_CLASSES
        self.device = device or self._get_device()
        self.model = None
        
        # Model configuration
        self.input_size = 640
        self.conf_threshold = 0.25
        self.iou_threshold = 0.45
        
    def _get_device(self) -> str:
        """Auto-detect best available device"""
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def load(self, model_path: Optional[str] = None) -> "IconDetector":
        """
        Load YOLO model.
        
        Args:
            model_path: Override model path
            
        Returns:
            Self for chaining
        """
        path = model_path or self.model_path
        
        if not Path(path).exists():
            logger.warning(f"Model not found at {path}, using pretrained yolo11n")
            path = "yolo11n.pt"
        
        self.model = YOLO(path)
        self.model.to(self.device)
        
        logger.info(f"Model loaded on {self.device}")
        return self
    
    def detect(
        self,
        image: np.ndarray,
        conf: Optional[float] = None,
        iou: Optional[float] = None
    ) -> List[Detection]:
        """
        Detect icons in image.
        
        Args:
            image: Input image (BGR numpy array)
            conf: Confidence threshold override
            iou: IOU threshold override
            
        Returns:
            List of Detection objects
        """
        if self.model is None:
            self.load()
        
        results = self.model.predict(
            source=image,
            conf=conf or self.conf_threshold,
            iou=iou or self.iou_threshold,
            imgsz=self.input_size,
            verbose=False
        )
        
        detections = []
        for result in results:
            for i in range(len(result.boxes)):
                box = result.boxes.xyxy[i].cpu().numpy()
                conf_score = float(result.boxes.conf[i].cpu().numpy())
                class_id = int(result.boxes.cls[i].cpu().numpy())
                
                class_name = (
                    self.class_names[class_id]
                    if class_id < len(self.class_names)
                    else f"class_{class_id}"
                )
                
                detections.append(Detection(
                    class_name=class_name,
                    class_id=class_id,
                    confidence=conf_score,
                    bbox=(float(box[0]), float(box[1]), float(box[2]), float(box[3]))
                ))
        
        return detections
    
    def __call__(self, image: np.ndarray, **kwargs) -> List[Detection]:
        """Shorthand for detect()"""
        return self.detect(image, **kwargs)
