"""
Configuration Management
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str = "yolo11n"
    input_size: int = 640
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 100


@dataclass
class TrainingConfig:
    """Training configuration"""
    epochs: int = 100
    batch_size: int = 16
    learning_rate: float = 0.01
    weight_decay: float = 0.0005
    momentum: float = 0.937
    optimizer: str = "SGD"


@dataclass
class DatasetConfig:
    """Dataset configuration"""
    name: str = "rico_icons"
    num_classes: int = 26
    train_split: float = 0.7
    val_split: float = 0.2
    test_split: float = 0.1
    class_names: list = field(default_factory=lambda: [
        "back_button", "search_icon", "menu_icon", "home_icon",
        "settings_icon", "share_icon", "delete_icon", "edit_icon",
        "add_icon", "close_icon", "favorite_icon", "profile_icon",
        "notification_icon", "camera_icon", "gallery_icon", "download_icon",
        "upload_icon", "play_icon", "pause_icon", "refresh_icon",
        "filter_icon", "sort_icon", "calendar_icon", "location_icon",
        "phone_icon", "email_icon"
    ])


@dataclass
class MultiModalConfig:
    """Multi-modal configuration"""
    enabled: bool = True
    ocr_engine: str = "easyocr"
    ocr_languages: list = field(default_factory=lambda: ["en"])
    proximity_threshold: int = 100


@dataclass
class Config:
    """Main configuration container"""
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    multimodal: MultiModalConfig = field(default_factory=MultiModalConfig)
    
    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file"""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(
            model=ModelConfig(**data.get("model", {})),
            training=TrainingConfig(**data.get("training", {})),
            dataset=DatasetConfig(**data.get("dataset", {})),
            multimodal=MultiModalConfig(**data.get("multimodal", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        from dataclasses import asdict
        return asdict(self)
    
    def save(self, path: str):
        """Save configuration to YAML file"""
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from file or return defaults"""
    if path and Path(path).exists():
        return Config.from_yaml(path)
    return Config()
