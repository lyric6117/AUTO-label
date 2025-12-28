# 任务 2.3：数据存储模块开发 - 执行计划

## 任务目标

实现检测结果和人工修正结果的持久化，支持 SQLite 数据库和文件系统存储。

## 执行内容

### 1. 实现 agent/storage.py

#### 功能需求
- SQLite 数据库初始化
- 表结构设计
- CRUD 操作接口
- 文件系统操作

#### 数据库表结构
1. **samples**：样本信息
   - id (主键)
   - image_path
   - dataset_version
   - created_at
   - updated_at

2. **detections**：检测结果
   - id (主键)
   - sample_id (外键)
   - class_name
   - confidence
   - bbox_x, bbox_y, bbox_w, bbox_h
   - decision_action
   - created_at

3. **reviews**：人工审核记录
   - id (主键)
   - detection_id (外键)
   - reviewer
   - action (accepted/modified/rejected)
   - modified_bbox (JSON)
   - reviewed_at

4. **versions**：数据集版本管理
   - id (主键)
   - version_name
   - parent_version
   - description
   - created_at

#### 文件系统操作
- 图片和标签文件存储
- 检测结果 JSON 存储
- 数据版本目录管理

## 执行步骤

1. 实现 DatabaseManager 类
   - __init__: 初始化数据库连接
   - _create_tables: 创建表结构
   - CRUD 操作方法

2. 实现 StorageManager 类
   - save_detection_result: 保存检测结果
   - save_review_result: 保存审核结果
   - get_review_queue: 获取待审核队列
   - move_to_final: 移动到最终目录

3. 创建测试脚本验证功能

## 验收标准

- ✅ 数据库表结构正确
- ✅ CRUD 操作正常
- ✅ 文件存储正确
- ✅ 数据版本管理正常

## 预计时间

30-40 分钟

## 依赖

任务 1.1（项目结构初始化）
任务 1.2（数据目录结构创建）
任务 1.3（配置文件准备）
