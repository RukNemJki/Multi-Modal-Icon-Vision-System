"""
OCR Engine Module
Text extraction using EasyOCR for mobile UI screenshots
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TextRegion:
    """Detected text region"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "bbox": list(self.bbox)
        }


class OCREngine:
    """
    OCR Engine using EasyOCR for text extraction.
    
    Implements text detection and recognition for mobile UI screenshots
    with preprocessing options for improved accuracy.
    """
    
    def __init__(
        self,
        languages: List[str] = None,
        gpu: bool = True
    ):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes (default: ['en'])
            gpu: Whether to use GPU acceleration
        """
        self.languages = languages or ["en"]
        self.gpu = gpu
        self._reader = None
    
    @property
    def reader(self):
        """Lazy-load EasyOCR reader"""
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.languages, gpu=self.gpu)
            logger.info(f"EasyOCR initialized: languages={self.languages}, gpu={self.gpu}")
        return self._reader
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input BGR image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Convert back to BGR
        return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
    
    def extract(
        self,
        image: np.ndarray,
        preprocess: bool = False
    ) -> List[TextRegion]:
        """
        Extract text from image.
        
        Args:
            image: Input BGR image
            preprocess: Apply preprocessing
            
        Returns:
            List of TextRegion objects
        """
        if preprocess:
            image = self.preprocess(image)
        
        results = self.reader.readtext(image)
        
        regions = []
        for bbox, text, conf in results:
            # Convert polygon to rectangle
            points = np.array(bbox, dtype=np.int32)
            x1, y1 = points.min(axis=0)
            x2, y2 = points.max(axis=0)
            
            regions.append(TextRegion(
                text=text.strip(),
                confidence=float(conf),
                bbox=(int(x1), int(y1), int(x2), int(y2))
            ))
        
        return regions
    
    def __call__(self, image: np.ndarray, **kwargs) -> List[TextRegion]:
        """Shorthand for extract()"""
        return self.extract(image, **kwargs)
