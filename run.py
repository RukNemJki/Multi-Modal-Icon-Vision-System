#!/usr/bin/env python
"""
Multi-Modal Icon Vision System
Main entry point for the application
"""

import sys
import argparse
from pathlib import Path


def check_requirements():
    """Verify required packages are installed"""
    required = ["flask", "torch", "ultralytics", "cv2", "yaml"]
    missing = []
    
    for pkg in required:
        try:
            __import__("cv2" if pkg == "cv2" else pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = True):
    """Start the Flask API server"""
    from src.api import create_app
    
    print("\n" + "=" * 50)
    print("🔍 Multi-Modal Icon Vision System")
    print("=" * 50)
    print(f"Server: http://{host}:{port}")
    print("Endpoints: /health, /predict, /analyze, /explain")
    print("=" * 50 + "\n")
    
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def run_analysis(image_path: str, output_path: str = None, ocr: bool = True):
    """Run analysis on a single image"""
    import cv2
    from src.core import MultiModalAnalyzer
    from src.utils import Visualizer
    
    print(f"Analyzing: {image_path}")
    
    analyzer = MultiModalAnalyzer()
    results = analyzer.analyze_file(image_path, enable_ocr=ocr)
    
    print(f"Found {results['stats']['num_icons']} icons")
    if ocr:
        print(f"Found {results['stats']['num_texts']} text regions")
    
    # Visualize
    if output_path:
        image = cv2.imread(image_path)
        vis = Visualizer()
        annotated = vis.visualize_results(image, results, output_path)
        print(f"Saved: {output_path}")
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Multi-Modal Icon Vision System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Start API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host address")
    server_parser.add_argument("--port", type=int, default=5000, help="Port number")
    server_parser.add_argument("--debug", action="store_true", help="Debug mode")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image")
    analyze_parser.add_argument("image", help="Path to image")
    analyze_parser.add_argument("-o", "--output", help="Output path for visualization")
    analyze_parser.add_argument("--no-ocr", action="store_true", help="Disable OCR")
    
    args = parser.parse_args()
    
    if not check_requirements():
        sys.exit(1)
    
    if args.command == "serve":
        run_server(args.host, args.port, args.debug)
    elif args.command == "analyze":
        run_analysis(args.image, args.output, not args.no_ocr)
    else:
        # Default: start server
        run_server()


if __name__ == "__main__":
    main()
