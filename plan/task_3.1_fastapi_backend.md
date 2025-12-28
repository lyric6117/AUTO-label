# 任务 3.1: FastAPI 后端开发

## 执行计划

### 目标
实现 FastAPI 后端服务，提供推理 API、审核队列 API 和统计 API，支持前端调用。

### 技术栈
- FastAPI: Web 框架
- uvicorn: ASGI 服务器
- pydantic: 数据验证
- Pillow: 图像处理

### 实现步骤

#### 步骤 1: 安装依赖
- 安装 fastapi
- 安装 uvicorn
- 安装 python-multipart (用于文件上传)
- 安装 Pillow

#### 步骤 2: 创建 API 模型定义
- 创建 api/models.py
- 定义请求和响应模型：
  - InferenceRequest: 推理请求模型
  - InferenceResponse: 推理响应模型
  - ReviewRequest: 审核请求模型
  - ReviewResponse: 审核响应模型
  - StatisticsResponse: 统计响应模型

#### 步骤 3: 实现推理 API
- 创建 api/inference_api.py
- 实现 POST /api/inference 端点
- 支持单张图片推理
- 支持批量图片推理
- 返回检测结果和决策信息

#### 步骤 4: 实现审核队列 API
- 创建 api/review_api.py
- 实现 GET /api/review/queue 端点：获取审核队列
- 实现 POST /api/review/{detection_id} 端点：提交审核结果
- 支持分页查询

#### 步骤 5: 实现统计 API
- 创建 api/stats_api.py
- 实现 GET /api/stats 端点：获取统计信息
- 返回样本数、检测数、决策统计、审核统计

#### 步骤 6: 创建主应用入口
- 创建 api/main.py
- 集成所有 API 路由
- 配置 CORS
- 添加健康检查端点

#### 步骤 7: 创建启动脚本
- 创建 run_api.py
- 配置 uvicorn 服务器
- 设置主机和端口

#### 步骤 8: 测试 API
- 创建 tests/test_api.py
- 测试推理 API
- 测试审核队列 API
- 测试统计 API

### API 端点设计

#### 推理 API
```
POST /api/inference
Content-Type: multipart/form-data

Request:
- file: 图片文件 (单张)
- files: 图片文件列表 (批量)

Response:
{
  "success": true,
  "data": {
    "image_path": "string",
    "detections": [
      {
        "cls": "string",
        "conf": float,
        "bbox": [float, float, float, float]
      }
    ],
    "decisions": [
      {
        "action": "auto_accept" | "send_to_review" | "discard",
        "confidence": float
      }
    ]
  }
}
```

#### 审核队列 API
```
GET /api/review/queue?limit=100&offset=0

Response:
{
  "success": true,
  "data": {
    "total": int,
    "items": [
      {
        "sample_id": int,
        "image_path": "string",
        "detection_id": int,
        "class_name": "string",
        "confidence": float,
        "bbox": [float, float, float, float],
        "decision_action": "string"
      }
    ]
  }
}

POST /api/review/{detection_id}
Content-Type: application/json

Request:
{
  "reviewer": "string",
  "action": "accepted" | "rejected" | "modified",
  "modified_bbox": {
    "x": float,
    "y": float,
    "w": float,
    "h": float
  }
}

Response:
{
  "success": true,
  "data": {
    "review_id": int
  }
}
```

#### 统计 API
```
GET /api/stats

Response:
{
  "success": true,
  "data": {
    "total_samples": int,
    "total_detections": int,
    "decision_stats": {
      "auto_accept": int,
      "send_to_review": int,
      "discard": int
    },
    "review_stats": {
      "accepted": int,
      "rejected": int,
      "modified": int
    }
  }
}
```

### 预期结果
- FastAPI 后端服务可以正常启动
- 推理 API 能够接收图片并返回检测结果
- 审核队列 API 能够获取待审核项目和提交审核结果
- 统计 API 能够返回系统统计信息
- 所有 API 端点通过测试

### 注意事项
- 使用 pydantic 进行数据验证
- 添加适当的错误处理
- 配置 CORS 以支持前端调用
- 使用异步处理提高性能
- 添加日志记录
- 确保线程安全
