# 任务 1.3：配置文件准备 - 执行计划

## 任务目标

定义 Agent 的决策规则和系统配置，提供可配置的参数管理。

## 执行内容

### 1. 创建主配置文件 config/agent_config.yaml

包含以下配置项：

#### 决策阈值配置
- auto_accept_threshold: 0.85（自动接受阈值）
- review_min_threshold: 0.4（审核最小阈值）
- discard_threshold: 0.4（丢弃阈值）

#### 模型配置
- name: "yolov8n"
- path: "models/yolov8n.pt"
- classes: 4 个类别

#### 数据存储配置
- base_path: "dataset"
- current_version: "v1_auto"
- db_path: "data/agent.db"

#### API 配置
- host: "0.0.0.0"
- port: 8000
- cors_origins: ["http://localhost:3000"]

### 2. 创建配置加载工具函数

在 utils/ 目录下创建 config_loader.py，实现：
- 加载 YAML 配置文件
- 配置验证
- 配置访问接口

## 执行步骤

1. 创建 config/agent_config.yaml 配置文件
2. 创建 utils/config_loader.py 配置加载工具
3. 测试配置加载功能

## 验收标准

- ✅ agent_config.yaml 内容完整且格式正确
- ✅ config_loader.py 可正确加载配置
- ✅ 配置访问接口正常工作

## 预计时间

10-15 分钟

## 依赖

任务 1.1（项目结构初始化）
任务 1.2（数据目录结构创建）
