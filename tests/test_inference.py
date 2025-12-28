import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.inference import InferenceCollector


def test_inference_collector():
    print("Testing InferenceCollector...")
    
    try:
        collector = InferenceCollector()
        print(f"Model loaded successfully from: {collector.model_path}")
        print(f"Classes: {collector.classes}")
        print(f"Confidence threshold: {collector.conf_threshold}")
        print(f"IOU threshold: {collector.iou_threshold}")
        
        test_image = "dataset/v0_seed/images/test.jpg"
        if Path(test_image).exists():
            result = collector.predict_single(test_image)
            print(f"\nInference result for {test_image}:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nTest image not found: {test_image}")
            print("Please place a test image at dataset/v0_seed/images/ to test inference.")
        
        print("\nInferenceCollector test completed successfully!")
        return True
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease ensure:")
        print("1. The YOLO model file exists at models/yolov8n.pt")
        print("2. Or update the model path in config/agent_config.yaml")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_inference_collector()
