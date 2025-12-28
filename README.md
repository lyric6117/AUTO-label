# YOLO标注代理系统

## 系统概述

YOLO标注代理系统是一个基于YOLO目标检测模型的智能标注辅助系统，通过置信度阈值自动决策检测结果的处理方式，减少人工审核工作量。

## 核心功能

### 1. 推理收集器 (InferenceCollector)
- 支持单张图片和批量图片推理
- 使用YOLOv8模型进行目标检测
- 标准化输出检测结果（类别、置信度、边界框）

### 2. 决策代理 (DecisionAgent)
- 基于置信度的三层决策机制：
  - **自动接受** (≥0.85): 高置信度检测结果直接接受
  - **待审核** (0.4-0.85): 中等置信度检测结果进入审核队列
  - **丢弃** (<0.4): 低置信度检测结果直接丢弃
- 支持按类别设置不同阈值
- 统计各决策类型的数量和比例

### 3. 存储管理 (StorageManager)
- SQLite数据库存储样本、检测、审核记录
- 文件系统管理图片和标注文件
- 支持数据版本管理（v0_seed, v1_auto等）

### 4. Web界面
- 纯HTML实现的轻量级前端界面
- 支持图片上传和实时推理
- 审核队列管理
- 统计信息展示

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 准备模型

将训练好的YOLO模型文件放置在 `models/` 目录下：

```
models/
  └── best.pt
```

### 3. 准备数据

将测试图片和标注文件放置在 `dataset/v0_seed/` 目录下：

```
dataset/
  └── v0_seed/
      ├── images/
      │   ├── image1.jpg
      │   └── image2.jpg
      └── labels/
          ├── image1.txt
          └── image2.txt
```

### 4. 配置系统

编辑 `config/agent_config.yaml` 文件，根据需要调整参数：

```yaml
model:
  path: "models/best.pt"
  classes:
    - "part1_normal"
    - "part1_fault"
    - "part2_normal"
    - "part2_fault"
  conf_threshold: 0.25
  iou_threshold: 0.45

decision:
  auto_accept_threshold: 0.85
  review_min_threshold: 0.4
  discard_threshold: 0.4
```

### 5. 运行批量推理

```bash
python run_batch_inference.py
```

这将处理 `dataset/v0_seed/images/` 目录下的所有图片，并将结果存储到数据库和文件系统中。

### 6. 启动API服务器

```bash
python run_api.py
```

服务器将在 http://localhost:8000 启动。

### 7. 打开Web界面

在浏览器中直接打开 `frontend/index.html` 文件（双击文件或右键选择浏览器打开），即可使用Web界面进行：
- 图片上传和推理
- 审核队列管理
- 统计信息查看

**注意**: 前端界面是纯HTML文件，不需要通过8000端口访问。8000端口是后端API服务器，前端通过JavaScript调用API接口。

## 目录结构

```
tf_infer/
├── agent/                  # 核心模块
│   ├── __init__.py
│   ├── inference.py        # 推理收集器
│   ├── decision.py         # 决策代理
│   └── storage.py          # 存储管理
├── api/                    # API接口
│   ├── __init__.py
│   ├── main.py             # FastAPI应用
│   ├── inference_api.py    # 推理API
│   ├── review_api.py       # 审核API
│   ├── stats_api.py        # 统计API
│   └── models.py           # 数据模型
├── frontend/               # 前端界面
│   └── index.html          # Web界面
├── config/                 # 配置文件
│   └── agent_config.yaml   # 系统配置
├── dataset/                # 数据集目录
│   ├── v0_seed/           # 种子数据
│   │   ├── images/
│   │   └── labels/
│   └── v1_auto/           # 自动标注数据
│       ├── auto_accept/
│       ├── human_fix/
│       └── review_queue/
├── models/                 # 模型文件
│   └── best.pt
├── utils/                  # 工具函数
│   ├── __init__.py
│   └── config_loader.py    # 配置加载器
├── tests/                  # 测试文件
│   ├── test_inference.py
│   ├── test_decision.py
│   ├── test_storage.py
│   └── test_api.py
├── data/                   # 数据目录
│   ├── agent.db            # SQLite数据库
│   └── temp/               # 临时文件
├── logs/                   # 日志目录
│   └── agent.log
├── run_api.py             # API服务器启动脚本
├── run_batch_inference.py # 批量推理脚本
└── requirements.txt       # Python依赖
```

## API接口

### 推理接口

**单张图片推理**
```
POST /api/inference
Content-Type: multipart/form-data

参数:
- file: 图片文件 (可选)
- image_path: 图片路径 (可选)

返回:
{
  "success": true,
  "data": {
    "image_path": "图片路径",
    "detections": [...],
    "decisions": [...]
  }
}
```

**批量图片推理**
```
POST /api/inference/batch
Content-Type: multipart/form-data

参数:
- files: 图片文件列表

返回:
{
  "success": true,
  "data": {
    "results": [...],
    "total": 10,
    "successful": 8
  }
}
```

### 审核接口

**获取审核队列**
```
GET /api/review/queue?limit=100&offset=0

返回:
{
  "success": true,
  "data": {
    "total": 5,
    "offset": 0,
    "limit": 100,
    "items": [...]
  }
}
```

**提交审核结果**
```
POST /api/review/sample/{sample_id}
Content-Type: application/json

{
  "reviewer": "user",
  "action": "accept"  # accept, reject, modify
}

返回:
{
  "success": true,
  "data": {
    "sample_id": 1,
    "action": "accept",
    "reviewed_count": 2
  }
}
```

**获取审核图片**
```
GET /api/review/image/{sample_id}

返回: 图片文件
```

### 统计接口

**获取统计信息**
```
GET /api/stats

返回:
{
  "success": true,
  "data": {
    "total_samples": 100,
    "total_detections": 250,
    "decision_stats": {
      "auto_accept": 150,
      "send_to_review": 80,
      "discard": 20
    },
    "review_stats": {
      "accepted": 60,
      "rejected": 15,
      "modified": 5
    }
  }
}
```

## 批量推理结果说明

运行 `python run_batch_inference.py` 后，系统会：

1. 读取 `dataset/v0_seed/images/` 目录下的所有图片
2. 对每张图片进行YOLO推理
3. 根据置信度阈值对检测结果进行决策
4. 将结果存储到数据库 `data/agent.db`
5. 根据决策结果将图片和标注文件复制到相应目录：
   - `dataset/v1_auto/auto_accept/`: 自动接受的样本
   - `dataset/v1_auto/review_queue/`: 待审核的样本

输出示例：
```
[1/5] 处理: 003740_2_24_1_10.jpg
  检测到 2 个目标
  决策: send_to_review

[2/5] 处理: 003740_2_7_1_4.jpg
  检测到 2 个目标
  决策: send_to_review

[3/5] 处理: 040928_8_7_1_1.jpg
  检测到 2 个目标
  决策: auto_accept

==================================================
批量推理总结
==================================================
总处理图片数: 5
自动接受: 3
待审核: 2
已丢弃: 0
==================================================
```

## 更换数据集

要处理新的数据集，只需：

1. 将新的图片和标注文件放入 `dataset/v0_seed/images/` 和 `dataset/v0_seed/labels/`
2. 运行 `python run_batch_inference.py`
3. 系统会自动处理新数据并更新数据库

## 配置说明

### 决策阈值

在 `config/agent_config.yaml` 中调整决策阈值：

```yaml
decision:
  auto_accept_threshold: 0.85    # 自动接受阈值
  review_min_threshold: 0.4     # 审核最小阈值
  discard_threshold: 0.4         # 丢弃阈值
```

### 模型配置

```yaml
model:
  name: "best"
  path: "models/best.pt"
  classes:
    - "part1_normal"
    - "part1_fault"
    - "part2_normal"
    - "part2_fault"
  conf_threshold: 0.25          # 置信度过滤阈值
  iou_threshold: 0.45            # NMS IOU阈值
```

### 存储配置

```yaml
storage:
  base_path: "dataset"
  current_version: "v1_auto"
  db_path: "data/agent.db"
```

## 后续扩展建议

1. **多视图架构支持**
   - 支持同一物体的多角度视图
   - 视图关联和融合

2. **标注编辑功能**
   - 在Web界面中直接编辑标注框
   - 支持添加、删除、修改标注

3. **数据增强**
   - 自动数据增强生成更多样本
   - 支持自定义增强策略

4. **模型迭代**
   - 支持模型版本管理
   - 自动模型训练和评估

5. **批量审核**
   - 支持批量接受/拒绝
   - 快捷键操作

6. **导出功能**
   - 导出为COCO、YOLO等格式
   - 支持自定义导出格式

## 常见问题

### Q: 如何修改决策阈值？
A: 编辑 `config/agent_config.yaml` 文件中的 `decision` 部分。

### Q: 如何添加新的类别？
A: 在 `config/agent_config.yaml` 的 `model.classes` 中添加新类别名称。

### Q: 如何查看数据库内容？
A: 使用SQLite工具打开 `data/agent.db` 文件，或使用API的统计接口。

### Q: 如何清理数据重新开始？
A: 删除 `data/agent.db` 和 `dataset/v1_auto/` 目录，然后重新运行批量推理。

## 技术栈

- **后端**: Python, FastAPI, Uvicorn
- **模型**: YOLOv8 (Ultralytics)
- **数据库**: SQLite
- **前端**: 纯HTML + JavaScript
- **配置**: YAML

## 许可证

MIT License
