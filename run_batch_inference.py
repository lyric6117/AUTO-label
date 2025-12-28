import sys
from pathlib import Path
import shutil
from typing import List, Dict, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.inference import InferenceCollector
from agent.decision import DecisionAgent
from agent.storage import StorageManager
from utils.config_loader import get_config


class BatchInference:
    def __init__(self):
        self.inference_collector = InferenceCollector()
        self.decision_agent = DecisionAgent()
        self.storage_manager = StorageManager()

    def run_batch_inference(self, image_dir: str) -> List[Dict[str, Any]]:
        image_path = Path(image_dir)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图片目录不存在: {image_dir}")
        
        image_files = list(image_path.glob("*.jpg")) + list(image_path.glob("*.jpeg")) + list(image_path.glob("*.png"))
        
        if not image_files:
            raise ValueError(f"目录中没有找到图片文件: {image_dir}")
        
        print(f"找到 {len(image_files)} 张图片")
        
        results = []
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 处理: {image_file.name}")
            
            try:
                detection_result = self.inference_collector.predict_single(str(image_file))
                
                if not detection_result or not detection_result.get('detections'):
                    print(f"  未检测到任何目标")
                    continue
                
                decision = self.decision_agent.decide(detection_result)
                
                self.storage_manager.save_detection_result(
                    str(image_file),
                    detection_result,
                    decision
                )
                
                result = {
                    'image_path': str(image_file),
                    'detection_count': len(detection_result['detections']),
                    'decision': decision
                }
                
                results.append(result)
                
                print(f"  检测到 {len(detection_result['detections'])} 个目标")
                print(f"  决策: {decision['overall_action']}")
                
            except Exception as e:
                print(f"  错误: {str(e)}")
                continue
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        print("\n" + "="*50)
        print("批量推理总结")
        print("="*50)
        print(f"总处理图片数: {len(results)}")
        
        auto_accept_count = sum(1 for r in results if r['decision']['overall_action'] == 'auto_accept')
        review_count = sum(1 for r in results if r['decision']['overall_action'] == 'send_to_review')
        discard_count = sum(1 for r in results if r['decision']['overall_action'] == 'discard')
        
        print(f"自动接受: {auto_accept_count}")
        print(f"待审核: {review_count}")
        print(f"已丢弃: {discard_count}")
        print("="*50)


def main():
    config = get_config()
    
    image_dir = Path(config.storage['base_path']) / "v0_seed" / "images"
    
    print(f"开始批量推理...")
    print(f"图片目录: {image_dir}")
    
    batch_inference = BatchInference()
    
    try:
        results = batch_inference.run_batch_inference(str(image_dir))
        batch_inference.print_summary(results)
        
        print("\n✓ 批量推理完成")
        
    except Exception as e:
        print(f"\n✗ 批量推理失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
