# 任务 1.2：数据目录结构创建 - 执行计划

## 任务目标

建立版本化的数据存储结构，支持数据集版本管理和样本来源追踪。

## 执行内容

### 1. 创建完整的数据集目录结构

```
dataset/
├── v0_seed/              # 初始种子数据（手动标注）
│   ├── images/
│   └── labels/
├── v1_auto/              # 第一轮自动标注
│   ├── auto_accept/      # 高置信度自动接受
│   │   ├── images/
│   │   └── labels/
│   ├── human_fix/        # 人工修正
│   │   ├── images/
│   │   └── labels/
│   └── review_queue/     # 待审核队列
│       ├── images/
│       └── detections/   # 原始检测结果 JSON
└── meta/                 # 元数据
    ├── dataset_versions.yaml
    └── sample_metadata.yaml
```

### 2. 创建配置文件模板

#### dataset_versions.yaml
记录数据集版本信息，包含：
- 版本号
- 创建时间
- 样本数量
- 来源说明
- 父版本

#### sample_metadata.yaml
样本来源标记模板，包含：
- 样本 ID
- 图片路径
- 标注来源（模型版本 + 人工修正）
- 审核人
- 审核时间

## 执行步骤

1. 创建 v0_seed 的 images 和 labels 子目录
2. 创建 v1_auto 的三个子目录及其子目录
3. 创建 dataset_versions.yaml 配置文件
4. 创建 sample_metadata.yaml 配置文件模板

## 验收标准

- ✅ 所有数据目录创建成功
- ✅ dataset_versions.yaml 内容完整
- ✅ sample_metadata.yaml 模板完整
- ✅ 目录结构与规划完全一致

## 预计时间

5-10 分钟

## 依赖

任务 1.1（项目结构初始化）
