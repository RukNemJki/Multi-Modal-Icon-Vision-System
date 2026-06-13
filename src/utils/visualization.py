"""
Visualization Utilities
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path


class Visualizer:
    """
    Visualization utilities for detection results.
    """
    
    # Color palette (BGR)
    COLORS = [
        (0, 255, 0),    # Green
        (255, 0, 0),    # Blue
        (0, 0, 255),    # Red
        (255, 255, 0),  # Cyan
        (0, 255, 255),  # Yellow
        (255, 0, 255),  # Magenta
        (128, 255, 0),  # Lime
        (255, 128, 0),  # Orange
        (0, 128, 255),  # Light Blue
        (255, 0, 128),  # Pink
    ]
    
    def __init__(self, font_scale: float = 0.5, thickness: int = 2):
        """
        Initialize visualizer.
        
        Args:
            font_scale: Text font scale
            thickness: Line thickness
        """
        self.font_scale = font_scale
        self.thickness = thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def get_color(self, idx: int) -> Tuple[int, int, int]:
        """Get color for class index"""
        return self.COLORS[idx % len(self.COLORS)]
    
    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Draw detection boxes on image.
        
        Args:
            image: Input image
            detections: List of detection dictionaries
            show_labels: Show class labels
            show_confidence: Show confidence scores
            
        Returns:
            Annotated image
        """
        img = image.copy()
        
        for det in detections:
            bbox = det["bbox"]
            x1, y1 = int(bbox["x1"]), int(bbox["y1"])
            x2, y2 = int(bbox["x2"]), int(bbox["y2"])
            
            class_id = det.get("class_id", 0)
            color = self.get_color(class_id)
            
            # Draw box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, self.thickness)
            
            # Draw label
            if show_labels:
                label = det.get("class_name", f"class_{class_id}")
                if show_confidence:
                    conf = det.get("confidence", 0)
                    label = f"{label}: {conf:.2f}"
                
                # Label background
                (tw, th), _ = cv2.getTextSize(label, self.font, self.font_scale, 1)
                cv2.rectangle(img, (x1, y1 - th - 4), (x1 + tw, y1), color, -1)
                cv2.putText(img, label, (x1, y1 - 4), self.font, self.font_scale, (255, 255, 255), 1)
        
        return img
    
    def draw_text_regions(
        self,
        image: np.ndarray,
        texts: List[Dict[str, Any]],
        color: Tuple[int, int, int] = (255, 0, 0)
    ) -> np.ndarray:
        """
        Draw text region boxes.
        
        Args:
            image: Input image
            texts: List of text region dictionaries
            color: Box color
            
        Returns:
            Annotated image
        """
        img = image.copy()
        
        for text in texts:
            bbox = text["bbox"]
            x1, y1, x2, y2 = bbox
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)
        
        return img
    
    def draw_correlations(
        self,
        image: np.ndarray,
        pairs: List[Dict[str, Any]],
        line_color: Tuple[int, int, int] = (0, 255, 255)
    ) -> np.ndarray:
        """
        Draw icon-text correlation lines.
        
        Args:
            image: Input image
            pairs: List of semantic pair dictionaries
            line_color: Line color
            
        Returns:
            Annotated image
        """
        img = image.copy()
        
        for pair in pairs:
            icon_bbox = pair["icon"]["bbox"]
            icon_cx = int((icon_bbox["x1"] + icon_bbox["x2"]) / 2)
            icon_cy = int((icon_bbox["y1"] + icon_bbox["y2"]) / 2)
            
            # Draw lines to nearby text (if available in extended data)
            for text in pair.get("nearby_text", []):
                # Draw icon center marker
                cv2.circle(img, (icon_cx, icon_cy), 4, line_color, -1)
        
        return img
    
    def visualize_results(
        self,
        image: np.ndarray,
        results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Visualize complete analysis results.
        
        Args:
            image: Input image
            results: Analysis results dictionary
            output_path: Path to save visualization
            
        Returns:
            Annotated image
        """
        img = image.copy()
        
        # Draw detections
        if "icons" in results:
            img = self.draw_detections(img, results["icons"])
        elif "detections" in results:
            img = self.draw_detections(img, results["detections"])
        
        # Draw text regions
        if "texts" in results:
            img = self.draw_text_regions(img, results["texts"])
        
        # Draw correlations
        if "pairs" in results:
            img = self.draw_correlations(img, results["pairs"])
        
        # Save if path provided
        if output_path:
            cv2.imwrite(output_path, img)
        
        return img
