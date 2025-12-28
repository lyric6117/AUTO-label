from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from ultralytics import YOLO
from utils.config_loader import get_config


class InferenceCollector:
    def __init__(self, model_path: Optional[str] = None):
        config = get_config()
        
        if model_path is None:
            model_path = config.model.get('path', 'models/yolov8n.pt')
        
        self.model_path = Path(model_path)
        self.classes = config.model.get('classes', [])
        self.conf_threshold = config.inference.get('conf_threshold', 0.25)
        self.iou_threshold = config.inference.get('iou_threshold', 0.45)
        self.device = config.inference.get('device', 'cpu')
        self.imgsz = config.inference.get('imgsz', 640)
        
        self.model = self._load_model()

    def _load_model(self) -> YOLO:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model = YOLO(str(self.model_path))
        return model

    def predict_single(self, image_path: str) -> Dict[str, Any]:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        results = self.model.predict(
            str(image_path),
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            imgsz=self.imgsz,
            verbose=False
        )
        
        return self._format_result(image_path.name, results[0])

    def predict_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        results_list = []
        
        for image_path in image_paths:
            try:
                result = self.predict_single(image_path)
                results_list.append(result)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                results_list.append({
                    "image": Path(image_path).name,
                    "detections": [],
                    "error": str(e)
                })
        
        return results_list

    def _format_result(self, image_name: str, result) -> Dict[str, Any]:
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xywh[0].tolist()
                
                class_name = self.classes[cls_id] if cls_id < len(self.classes) else f"class_{cls_id}"
                
                detection = {
                    "cls": class_name,
                    "conf": conf,
                    "bbox": bbox
                }
                
                if self._validate_detection(detection):
                    detections.append(detection)
        
        return {
            "image": image_name,
            "detections": detections
        }

    def _validate_detection(self, detection: Dict[str, Any]) -> bool:
        bbox = detection.get("bbox", [])
        conf = detection.get("conf", 0.0)
        
        if not self._validate_bbox(bbox):
            return False
        
        if not self._validate_confidence(conf):
            return False
        
        return True

    def _validate_bbox(self, bbox: List[float]) -> bool:
        if len(bbox) != 4:
            return False
        
        x, y, w, h = bbox
        
        if w <= 0 or h <= 0:
            return False
        
        if not all(isinstance(v, (int, float)) for v in bbox):
            return False
        
        return True

    def _validate_confidence(self, conf: float) -> bool:
        return 0.0 <= conf <= 1.0

    def save_results(self, results: List[Dict[str, Any]], output_dir: str):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for result in results:
            image_name = result["image"]
            json_name = Path(image_name).stem + ".json"
            json_path = output_dir / json_name
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
