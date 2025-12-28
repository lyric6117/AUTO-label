# 任务 2.2：决策 Agent 模块开发 - 执行计划

## 任务目标

实现基于置信度的自动决策逻辑，决定哪些检测结果需要人工审核。

## 执行内容

### 1. 实现 agent/decision.py

#### 功能需求
- 基于置信度的三级决策：
  - conf >= 0.85: auto_accept（自动接受）
  - 0.4 <= conf < 0.85: send_to_review（发送到审核队列）
  - conf < 0.4: discard（丢弃）
- 批量决策接口
- 决策统计功能（接受/审核/丢弃数量）

#### 决策规则
```python
if conf >= auto_accept_threshold:
    action = "auto_accept"
elif review_min_threshold <= conf < auto_accept_threshold:
    action = "send_to_review"
else:
    action = "discard"
```

#### 决策策略扩展
- 支持基于类别的差异化阈值
- 支持后续添加更复杂的决策规则

### 2. 实现决策统计功能
- 统计每个决策类别的数量
- 统计每个类别的决策分布
- 生成决策报告

## 执行步骤

1. 实现 DecisionAgent 类
   - __init__: 加载配置和阈值
   - decide_single: 单个检测结果的决策
   - decide_batch: 批量决策
   - get_statistics: 获取决策统计信息

2. 实现决策策略扩展接口
   - _get_class_threshold: 获取类别特定的阈值
   - _apply_custom_rules: 应用自定义规则

3. 创建测试脚本验证功能

## 验收标准

- ✅ 决策逻辑正确
- ✅ 统计功能完整
- ✅ 支持类别差异化阈值
- ✅ 决策结果格式正确

## 预计时间

20-30 分钟

## 依赖

任务 1.1（项目结构初始化）
任务 1.3（配置文件准备）
任务 2.1（推理采集模块开发）
