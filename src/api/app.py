"""
Flask REST API for Icon Detection Service
"""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ..core import IconDetector, MultiModalAnalyzer


def create_app(config: Optional[dict] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    cfg = config or {}
    app.config["MAX_CONTENT_LENGTH"] = cfg.get("max_upload_mb", 10) * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = cfg.get("upload_folder", "uploads")
    app.config["RESULTS_FOLDER"] = cfg.get("results_folder", "results")
    
    # Create directories
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["RESULTS_FOLDER"]).mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    model_path = cfg.get("model_path", "models/best_icon_detector.pt")
    detector = IconDetector(model_path)
    analyzer = MultiModalAnalyzer(model_path)
    
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    
    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    
    # ============ Routes ============
    
    @app.route("/", methods=["GET"])
    def index():
        """API information"""
        return jsonify({
            "name": "Multi-Modal Icon Vision API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": ["/health", "/predict", "/analyze", "/explain", "/classes"]
        })
    
    @app.route("/health", methods=["GET"])
    def health():
        """Health check for container orchestration"""
        import torch
        return jsonify({
            "status": "healthy",
            "model_loaded": detector.model is not None,
            "cuda_available": torch.cuda.is_available(),
            "device": detector.device,
            "architecture": "YOLOv11 Nano"
        })
    
    @app.route("/classes", methods=["GET"])
    def classes():
        """List supported icon classes"""
        return jsonify({
            "num_classes": len(detector.class_names),
            "classes": detector.class_names
        })
    
    @app.route("/predict", methods=["POST"])
    def predict():
        """Run icon detection on uploaded image"""
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{timestamp}_{filename}")
            file.save(filepath)
            
            # Get parameters
            conf = request.form.get("confidence", type=float, default=0.25)
            iou = request.form.get("iou", type=float, default=0.45)
            
            # Run detection
            image = cv2.imread(filepath)
            h, w = image.shape[:2]
            
            detections = detector.detect(image, conf=conf, iou=iou)
            
            return jsonify({
                "image": {"width": w, "height": h, "filename": filename},
                "detections": [d.to_dict() for d in detections],
                "num_detections": len(detections),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/analyze", methods=["POST"])
    def analyze():
        """Run multi-modal analysis (detection + OCR)"""
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{timestamp}_{filename}")
            file.save(filepath)
            
            # Get parameters
            conf = request.form.get("confidence", type=float, default=0.25)
            iou = request.form.get("iou", type=float, default=0.45)
            enable_ocr = request.form.get("ocr", type=bool, default=True)
            
            # Run analysis
            result = analyzer.analyze_file(filepath, enable_ocr=enable_ocr, conf=conf, iou=iou)
            result["timestamp"] = datetime.now().isoformat()
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/explain", methods=["POST"])
    def explain():
        """Get human-readable explanations for detections"""
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{timestamp}_{filename}")
            file.save(filepath)
            
            # Run detection
            image = cv2.imread(filepath)
            detections = detector.detect(image)
            
            # Generate explanations
            explanations = []
            for det in detections:
                base_name = det.class_name.replace("_", " ").replace("icon", "").replace("button", "").strip()
                explanations.append({
                    "icon": det.class_name,
                    "confidence": det.confidence,
                    "bbox": det.to_dict()["bbox"],
                    "accessibility_label": base_name.title(),
                    "rationale": f"Detected {base_name} with {det.confidence*100:.1f}% confidence"
                })
            
            return jsonify({
                "explanations": explanations,
                "num_detections": len(explanations),
                "model": "YOLOv11 Nano",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/results/<filename>", methods=["GET"])
    def get_result(filename):
        """Serve result images"""
        return send_from_directory(app.config["RESULTS_FOLDER"], filename)
    
    return app


# Standalone server
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
