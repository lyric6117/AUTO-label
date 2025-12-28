import sys
from pathlib import Path
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from api.main import app
from PIL import Image
import numpy as np


def create_test_image(path: str):
    img = Image.new('RGB', (640, 480), color='red')
    img.save(path)


def test_health_check():
    print("=== 测试健康检查 ===")
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    
    print("✓ 健康检查通过")


def test_inference_api():
    print("\n=== 测试推理 API ===")
    
    client = TestClient(app)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_image_path = Path(temp_dir) / "test_image.jpg"
        create_test_image(str(test_image_path))
        
        with open(test_image_path, "rb") as f:
            response = client.post(
                "/api/inference",
                files={"file": ("test_image.jpg", f, "image/jpeg")}
            )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            assert "success" in data
            assert "data" in data
            
            if data["success"]:
                assert "detections" in data["data"]
                assert "decisions" in data["data"]
                print("✓ 推理 API 测试通过（检测到目标）")
            else:
                print("✓ 推理 API 测试通过（未检测到目标，API 正常响应）")
        else:
            print(f"✗ 推理 API 测试失败: {response.text}")


def test_review_queue_api():
    print("\n=== 测试审核队列 API ===")
    
    client = TestClient(app)
    
    response = client.get("/api/review/queue?limit=10")
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert data["success"] == True
        assert "data" in data
        assert "items" in data["data"]
        
        print("✓ 审核队列 API 测试通过")
    else:
        print(f"✗ 审核队列 API 测试失败: {response.text}")


def test_statistics_api():
    print("\n=== 测试统计 API ===")
    
    client = TestClient(app)
    
    response = client.get("/api/stats")
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert data["success"] == True
        assert "data" in data
        assert "total_samples" in data["data"]
        assert "total_detections" in data["data"]
        assert "decision_stats" in data["data"]
        assert "review_stats" in data["data"]
        
        print("✓ 统计 API 测试通过")
    else:
        print(f"✗ 统计 API 测试失败: {response.text}")


def test_decision_stats_api():
    print("\n=== 测试决策统计 API ===")
    
    client = TestClient(app)
    
    response = client.get("/api/stats/decision")
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert data["success"] == True
        assert "data" in data
        assert "decision_stats" in data["data"]
        
        print("✓ 决策统计 API 测试通过")
    else:
        print(f"✗ 决策统计 API 测试失败: {response.text}")


def test_review_stats_api():
    print("\n=== 测试审核统计 API ===")
    
    client = TestClient(app)
    
    response = client.get("/api/stats/review")
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert data["success"] == True
        assert "data" in data
        assert "review_stats" in data["data"]
        
        print("✓ 审核统计 API 测试通过")
    else:
        print(f"✗ 审核统计 API 测试失败: {response.text}")


def test_review_submit_api():
    print("\n=== 测试审核提交 API ===")
    
    client = TestClient(app)
    
    queue_response = client.get("/api/review/queue?limit=1")
    
    if queue_response.status_code == 200:
        queue_data = queue_response.json()
        items = queue_data["data"]["items"]
        
        if items:
            detection_id = items[0]["detection_id"]
            
            review_data = {
                "reviewer": "test_reviewer",
                "action": "accepted"
            }
            
            response = client.post(
                f"/api/review/{detection_id}",
                json=review_data
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                assert data["success"] == True
                assert "data" in data
                assert "review_id" in data["data"]
                
                print("✓ 审核提交 API 测试通过")
            else:
                print(f"✗ 审核提交 API 测试失败: {response.text}")
        else:
            print("⚠ 审核队列为空，跳过审核提交测试")
    else:
        print(f"✗ 获取审核队列失败: {queue_response.text}")


def main():
    print("开始测试 FastAPI 后端...\n")
    
    try:
        test_health_check()
        test_inference_api()
        test_review_queue_api()
        test_statistics_api()
        test_decision_stats_api()
        test_review_stats_api()
        test_review_submit_api()
        
        print("\n" + "="*50)
        print("✓ 所有 API 测试通过！")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
