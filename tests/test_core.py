"""
Unit Tests for Multi-Modal Icon Vision System
"""

import unittest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfiguration(unittest.TestCase):
    """Test configuration loading"""
    
    def test_config_exists(self):
        """Config file exists"""
        self.assertTrue(os.path.exists("config/config.yaml"))
    
    def test_config_loads(self):
        """Config loads correctly"""
        from src.utils.config import load_config
        config = load_config("config/config.yaml")
        self.assertEqual(config.model.name, "yolo11n")
        self.assertEqual(config.dataset.num_classes, 26)


class TestDetector(unittest.TestCase):
    """Test icon detector"""
    
    def test_detector_init(self):
        """Detector initializes"""
        from src.core.detector import IconDetector
        detector = IconDetector()
        self.assertEqual(len(detector.class_names), 26)
    
    def test_default_classes(self):
        """Default classes are correct"""
        from src.core.detector import IconDetector
        detector = IconDetector()
        self.assertIn("search_icon", detector.class_names)
        self.assertIn("menu_icon", detector.class_names)


class TestAnalyzer(unittest.TestCase):
    """Test multi-modal analyzer"""
    
    def test_analyzer_init(self):
        """Analyzer initializes"""
        from src.core.analyzer import MultiModalAnalyzer
        analyzer = MultiModalAnalyzer()
        self.assertEqual(analyzer.proximity_threshold, 100)
    
    def test_keywords_defined(self):
        """Semantic keywords are defined"""
        from src.core.analyzer import MultiModalAnalyzer
        self.assertIn("search_icon", MultiModalAnalyzer.KEYWORDS)


class TestAPI(unittest.TestCase):
    """Test Flask API"""
    
    def test_app_creates(self):
        """App creates successfully"""
        from src.api import create_app
        app = create_app()
        self.assertIsNotNone(app)
    
    def test_health_endpoint(self):
        """Health endpoint responds"""
        from src.api import create_app
        app = create_app()
        with app.test_client() as client:
            response = client.get("/health")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["status"], "healthy")


class TestImports(unittest.TestCase):
    """Test package imports"""
    
    def test_import_core(self):
        """Core imports work"""
        from src.core import IconDetector, OCREngine, MultiModalAnalyzer
        self.assertIsNotNone(IconDetector)
        self.assertIsNotNone(OCREngine)
        self.assertIsNotNone(MultiModalAnalyzer)
    
    def test_import_api(self):
        """API imports work"""
        from src.api import create_app
        self.assertIsNotNone(create_app)
    
    def test_import_utils(self):
        """Utils imports work"""
        from src.utils import Visualizer, Config
        self.assertIsNotNone(Visualizer)
        self.assertIsNotNone(Config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
