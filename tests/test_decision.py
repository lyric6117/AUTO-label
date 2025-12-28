import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.decision import DecisionAgent


def test_decision_agent():
    print("Testing DecisionAgent...")
    
    agent = DecisionAgent()
    
    print(f"\nDecision thresholds:")
    print(f"  Auto accept: {agent.auto_accept_threshold}")
    print(f"  Review min: {agent.review_min_threshold}")
    print(f"  Discard: {agent.discard_threshold}")
    
    test_detections = [
        {"cls": "part1_normal", "conf": 0.92, "bbox": [100, 100, 50, 50]},
        {"cls": "part1_fault", "conf": 0.88, "bbox": [200, 200, 60, 60]},
        {"cls": "part2_normal", "conf": 0.75, "bbox": [150, 150, 40, 40]},
        {"cls": "part2_fault", "conf": 0.50, "bbox": [300, 300, 70, 70]},
        {"cls": "part1_normal", "conf": 0.35, "bbox": [50, 50, 30, 30]},
    ]
    
    print("\nTesting single detection decisions:")
    for i, detection in enumerate(test_detections, 1):
        action = agent.decide_single(detection)
        print(f"  Detection {i}: {detection['cls']} (conf={detection['conf']:.2f}) -> {action.value}")
    
    agent.reset_statistics()
    
    print("\nTesting batch decision:")
    actions = agent.decide_batch(test_detections)
    for i, (detection, action) in enumerate(zip(test_detections, actions), 1):
        print(f"  Detection {i}: {detection['cls']} (conf={detection['conf']:.2f}) -> {action.value}")
    
    print("\nTesting image decision:")
    image_result = {
        "image": "test_image.jpg",
        "detections": test_detections
    }
    
    image_decision = agent.decide_image(image_result)
    print(f"  Image: {image_decision['image']}")
    print(f"  Summary: {image_decision['summary']}")
    
    print("\nDecision statistics:")
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\nDecisionAgent test completed successfully!")
    return True


if __name__ == "__main__":
    test_decision_agent()
