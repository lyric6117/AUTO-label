from ultralytics import YOLO
from pathlib import Path


def download_pretrained_model():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "yolov8n.pt"
    
    if model_path.exists():
        print(f"Model already exists at: {model_path}")
        return str(model_path)
    
    print("Downloading YOLOv8n pretrained model...")
    model = YOLO('yolov8n.pt')
    
    model.save(str(model_path))
    print(f"Model saved to: {model_path}")
    
    return str(model_path)


if __name__ == "__main__":
    download_pretrained_model()
