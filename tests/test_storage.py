import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.storage import DatabaseManager, StorageManager
from utils.config_loader import get_config


def test_database_manager():
    print("=== 测试 DatabaseManager ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = Path(temp_dir) / "test_agent.db"
        db = DatabaseManager(str(test_db_path))
        
        print("✓ 数据库初始化成功")
        
        sample_id = db.insert_sample("test_image.jpg", "v1_auto")
        print(f"✓ 插入样本成功，ID: {sample_id}")
        
        detection = {
            'cls': 'person',
            'conf': 0.92,
            'bbox': [100, 150, 200, 300]
        }
        
        detection_id = db.insert_detection(sample_id, detection, 'auto_accept')
        print(f"✓ 插入检测结果成功，ID: {detection_id}")
        
        review_id = db.insert_review(detection_id, 'reviewer1', 'accepted')
        print(f"✓ 插入审核结果成功，ID: {review_id}")
        
        version_id = db.insert_version('v1_auto', 'v0_seed', 'Auto-annotated version')
        print(f"✓ 插入版本信息成功，ID: {version_id}")
        
        stats = db.get_statistics()
        print(f"✓ 获取统计信息成功:")
        print(f"  - 总样本数: {stats['total_samples']}")
        print(f"  - 总检测数: {stats['total_detections']}")
        print(f"  - 决策统计: {stats['decision_stats']}")
        print(f"  - 审核统计: {stats['review_stats']}")
        
        print("✓ 数据库测试完成")


def test_database_manager_review_queue():
    print("\n=== 测试审核队列功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = Path(temp_dir) / "test_queue.db"
        db = DatabaseManager(str(test_db_path))
        
        sample_id1 = db.insert_sample("test_image1.jpg", "v1_auto")
        sample_id2 = db.insert_sample("test_image2.jpg", "v1_auto")
        
        detection1 = {'cls': 'person', 'conf': 0.6, 'bbox': [100, 150, 200, 300]}
        detection2 = {'cls': 'car', 'conf': 0.95, 'bbox': [50, 80, 150, 200]}
        detection3 = {'cls': 'dog', 'conf': 0.5, 'bbox': [200, 250, 300, 400]}
        
        db.insert_detection(sample_id1, detection1, 'send_to_review')
        db.insert_detection(sample_id1, detection2, 'auto_accept')
        db.insert_detection(sample_id2, detection3, 'send_to_review')
        
        review_queue = db.get_review_queue()
        print(f"✓ 获取审核队列成功，队列长度: {len(review_queue)}")
        
        for item in review_queue:
            print(f"  - 样本ID: {item['sample_id']}, 类别: {item['class_name']}, 置信度: {item['confidence']:.2f}")
        
        print("✓ 审核队列测试完成")


def test_storage_manager():
    print("\n=== 测试 StorageManager ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_config = {
            'storage': {
                'base_path': temp_dir,
                'current_version': 'v1_test',
                'db_path': str(Path(temp_dir) / 'test_agent.db')
            }
        }
        
        original_config = get_config()
        import utils.config_loader
        utils.config_loader._config_cache = test_config
        
        try:
            storage = StorageManager()
            print("✓ StorageManager 初始化成功")
            
            detection_result = {
                'image_path': 'test.jpg',
                'detections': [
                    {'cls': 'person', 'conf': 0.92, 'bbox': [100, 150, 200, 300]},
                    {'cls': 'car', 'conf': 0.6, 'bbox': [50, 80, 150, 200]}
                ]
            }
            
            decision = {
                'decisions': [
                    {'action': 'auto_accept', 'confidence': 0.92},
                    {'action': 'send_to_review', 'confidence': 0.6}
                ]
            }
            
            print("✓ 保存检测结果...")
            storage.save_detection_result('test.jpg', detection_result, decision)
            
            stats = storage.get_statistics()
            print(f"✓ 获取统计信息成功:")
            print(f"  - 总样本数: {stats['total_samples']}")
            print(f"  - 总检测数: {stats['total_detections']}")
            print(f"  - 决策统计: {stats['decision_stats']}")
            
            review_queue = storage.get_review_queue()
            print(f"✓ 获取审核队列成功，队列长度: {len(review_queue)}")
            
            print("✓ StorageManager 测试完成")
            
        finally:
            utils.config_loader._config_cache = original_config


def test_storage_manager_file_operations():
    print("\n=== 测试文件操作 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_image_dir = Path(temp_dir) / 'source_images'
        test_image_dir.mkdir(parents=True, exist_ok=True)
        
        test_image_path = test_image_dir / 'test_image.jpg'
        test_image_path.write_text('fake image content')
        
        test_config = {
            'storage': {
                'base_path': temp_dir,
                'current_version': 'v1_test',
                'db_path': str(Path(temp_dir) / 'test_agent.db')
            }
        }
        
        original_config = get_config()
        import utils.config_loader
        utils.config_loader._config_cache = test_config
        
        try:
            storage = StorageManager()
            
            detection_result = {
                'image_path': str(test_image_path),
                'detections': [
                    {'cls': 'person', 'conf': 0.6, 'bbox': [100, 150, 200, 300]}
                ]
            }
            
            decision = {
                'decisions': [
                    {'action': 'send_to_review', 'confidence': 0.6}
                ]
            }
            
            storage.save_detection_result(str(test_image_path), detection_result, decision)
            print("✓ 保存检测结果并复制到审核队列")
            
            review_queue = storage.get_review_queue()
            if review_queue:
                print(f"✓ 审核队列中有 {len(review_queue)} 个待审核项目")
            
            print("✓ 文件操作测试完成")
            
        finally:
            utils.config_loader._config_cache = original_config


def main():
    print("开始测试存储模块...\n")
    
    try:
        test_database_manager()
        test_database_manager_review_queue()
        test_storage_manager()
        test_storage_manager_file_operations()
        
        print("\n" + "="*50)
        print("✓ 所有测试通过！")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
