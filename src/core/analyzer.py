"""
Multi-Modal Analyzer Module
Combines visual detection with OCR for semantic UI understanding
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import logging

from .detector import IconDetector, Detection
from .ocr import OCREngine, TextRegion

logger = logging.getLogger(__name__)


@dataclass
class SemanticPair:
    """Icon-text correlation result"""
    icon: Detection
    nearby_text: List[str]
    spatial_relation: str  # 'left', 'right', 'above', 'below', 'none'
    semantic_score: float
    semantic_label: str
    
    def to_dict(self) -> dict:
        return {
            "icon": self.icon.to_dict(),
            "nearby_text": self.nearby_text,
            "spatial_relation": self.spatial_relation,
            "semantic_score": round(self.semantic_score, 4),
            "semantic_label": self.semantic_label
        }


class MultiModalAnalyzer:
    """
    Multi-Modal UI Analyzer.
    
    Combines YOLOv11 icon detection with EasyOCR text extraction
    to provide semantic understanding of mobile UI elements.
    
    Key features:
    - Icon-text spatial correlation (100px threshold)
    - Semantic scoring based on keyword matching
    - Contextual label generation
    """
    
    # Semantic keywords for each icon class
    KEYWORDS = {
        "back_button": ["back", "return", "previous"],
        "search_icon": ["search", "find", "look"],
        "menu_icon": ["menu", "options", "more"],
        "home_icon": ["home", "main", "dashboard"],
        "settings_icon": ["settings", "preferences", "config"],
        "share_icon": ["share", "send", "forward"],
        "delete_icon": ["delete", "remove", "trash"],
        "edit_icon": ["edit", "modify", "change"],
        "add_icon": ["add", "new", "create", "plus"],
        "close_icon": ["close", "exit", "cancel"],
        "favorite_icon": ["favorite", "like", "heart", "save"],
        "profile_icon": ["profile", "account", "user"],
        "notification_icon": ["notification", "alert", "bell"],
        "camera_icon": ["camera", "photo", "capture"],
        "gallery_icon": ["gallery", "photos", "images"],
        "download_icon": ["download", "save", "get"],
        "upload_icon": ["upload", "send", "submit"],
        "play_icon": ["play", "start", "watch"],
        "pause_icon": ["pause", "stop", "hold"],
        "refresh_icon": ["refresh", "reload", "sync"],
        "filter_icon": ["filter", "refine", "narrow"],
        "sort_icon": ["sort", "order", "arrange"],
        "calendar_icon": ["calendar", "date", "schedule"],
        "location_icon": ["location", "map", "place"],
        "phone_icon": ["phone", "call", "dial"],
        "email_icon": ["email", "mail", "message"]
    }
    
    def __init__(
        self,
        model_path: str = "models/best_icon_detector.pt",
        proximity_threshold: int = 100,
        ocr_languages: List[str] = None
    ):
        """
        Initialize multi-modal analyzer.
        
        Args:
            model_path: Path to YOLO model
            proximity_threshold: Max pixel distance for icon-text correlation
            ocr_languages: Languages for OCR
        """
        self.detector = IconDetector(model_path)
        self.ocr = OCREngine(languages=ocr_languages)
        self.proximity_threshold = proximity_threshold
    
    def _distance(
        self,
        icon_bbox: Tuple[float, float, float, float],
        text_bbox: Tuple[int, int, int, int]
    ) -> float:
        """Calculate center-to-center distance between boxes"""
        icon_cx = (icon_bbox[0] + icon_bbox[2]) / 2
        icon_cy = (icon_bbox[1] + icon_bbox[3]) / 2
        text_cx = (text_bbox[0] + text_bbox[2]) / 2
        text_cy = (text_bbox[1] + text_bbox[3]) / 2
        
        return np.sqrt((icon_cx - text_cx)**2 + (icon_cy - text_cy)**2)
    
    def _spatial_relation(
        self,
        icon_bbox: Tuple[float, float, float, float],
        text_bbox: Tuple[int, int, int, int]
    ) -> str:
        """Determine spatial relationship between icon and text"""
        icon_cx = (icon_bbox[0] + icon_bbox[2]) / 2
        icon_cy = (icon_bbox[1] + icon_bbox[3]) / 2
        text_cx = (text_bbox[0] + text_bbox[2]) / 2
        text_cy = (text_bbox[1] + text_bbox[3]) / 2
        
        dx, dy = text_cx - icon_cx, text_cy - icon_cy
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "below" if dy > 0 else "above"
    
    def _semantic_score(self, icon_class: str, texts: List[str]) -> float:
        """Calculate semantic relevance score"""
        keywords = self.KEYWORDS.get(icon_class, [])
        if not keywords or not texts:
            return 0.0
        
        combined = " ".join(texts).lower()
        matches = sum(1 for kw in keywords if kw in combined)
        return min(matches / len(keywords), 1.0)
    
    def _semantic_label(self, icon_class: str, texts: List[str]) -> str:
        """Generate human-readable semantic label"""
        base = icon_class.replace("_", " ").replace("icon", "").replace("button", "").strip().title()
        
        if texts and len(texts[0]) < 30:
            return f"{base}: {texts[0]}"
        return base
    
    def correlate(
        self,
        icons: List[Detection],
        texts: List[TextRegion]
    ) -> List[SemanticPair]:
        """
        Correlate icons with nearby text.
        
        Args:
            icons: Icon detections
            texts: Text regions
            
        Returns:
            List of SemanticPair objects
        """
        pairs = []
        
        for icon in icons:
            nearby = []
            relations = []
            
            for text in texts:
                dist = self._distance(icon.bbox, text.bbox)
                if dist <= self.proximity_threshold:
                    nearby.append(text.text)
                    relations.append(self._spatial_relation(icon.bbox, text.bbox))
            
            # Primary spatial relationship
            relation = "none"
            if relations:
                relation = Counter(relations).most_common(1)[0][0]
            
            pairs.append(SemanticPair(
                icon=icon,
                nearby_text=nearby,
                spatial_relation=relation,
                semantic_score=self._semantic_score(icon.class_name, nearby),
                semantic_label=self._semantic_label(icon.class_name, nearby)
            ))
        
        return pairs
    
    def analyze(
        self,
        image: np.ndarray,
        enable_ocr: bool = True,
        conf: float = 0.25,
        iou: float = 0.45
    ) -> Dict[str, Any]:
        """
        Run complete multi-modal analysis.
        
        Args:
            image: Input BGR image
            enable_ocr: Whether to run OCR
            conf: Detection confidence threshold
            iou: NMS IOU threshold
            
        Returns:
            Analysis results dictionary
        """
        h, w = image.shape[:2]
        
        # Icon detection
        icons = self.detector.detect(image, conf=conf, iou=iou)
        logger.info(f"Detected {len(icons)} icons")
        
        # OCR and correlation
        texts = []
        pairs = []
        
        if enable_ocr:
            texts = self.ocr.extract(image)
            logger.info(f"Extracted {len(texts)} text regions")
            pairs = self.correlate(icons, texts)
        
        return {
            "image": {"width": w, "height": h},
            "icons": [i.to_dict() for i in icons],
            "texts": [t.to_dict() for t in texts],
            "pairs": [p.to_dict() for p in pairs],
            "stats": {
                "num_icons": len(icons),
                "num_texts": len(texts),
                "ocr_enabled": enable_ocr
            }
        }
    
    def analyze_file(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """Analyze image from file path"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        result = self.analyze(image, **kwargs)
        result["image"]["path"] = image_path
        return result
