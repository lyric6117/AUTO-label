# 模型文件说明

请将您的 YOLO 模型文件放置在此目录下。

默认配置期望的模型文件：
- yolov8n.pt（YOLOv8 Nano 模型）

如果您使用其他模型文件，请更新 `config/agent_config.yaml` 中的 `model.path` 配置项。

## 获取预训练模型

如果您没有训练好的模型，可以从 Ultralytics 下载预训练模型：

```bash
# 下载 YOLOv8n
yolo export model=yolov8n.pt format=onnx

# 或者直接使用 Python 代码
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.save('models/yolov8n.pt')
```

## 自定义模型

如果您有自己训练的模型，请将模型文件复制到此目录：
- 支持的格式：.pt, .onnx, .engine
- 确保模型类别与配置文件中的 classes 定义一致
