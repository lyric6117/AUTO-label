# 任务 3.2: React 前端开发

## 执行计划

### 目标
实现 React 前端界面，提供图片标注、审核队列管理和统计展示功能。

### 技术栈
- React: 前端框架
- TypeScript: 类型安全
- Vite: 构建工具
- Axios: HTTP 客户端
- React Router: 路由管理
- Ant Design: UI 组件库
- React Konva: 画布绘制（用于标注）

### 实现步骤

#### 步骤 1: 初始化前端项目
- 使用 Vite 创建 React + TypeScript 项目
- 安装依赖：axios, react-router-dom, antd, @ant-design/icons, react-konva, konva
- 配置项目结构

#### 步骤 2: 创建基础布局和路由
- 创建 App 组件
- 配置路由：首页、推理页面、审核页面、统计页面
- 创建导航栏和布局组件

#### 步骤 3: 实现推理页面
- 创建图片上传组件
- 实现推理结果展示
- 显示检测框和置信度
- 显示决策结果（自动接受、待审核、丢弃）

#### 步骤 4: 实现审核队列页面
- 创建审核队列列表组件
- 实现图片预览功能
- 创建标注编辑器（使用 React Konva）
- 实现审核操作（接受、拒绝、修改）
- 支持分页加载

#### 步骤 5: 实现统计页面
- 创建统计卡片组件
- 实现决策统计图表
- 实现审核统计图表
- 显示总体统计信息

#### 步骤 6: 创建 API 服务层
- 创建 API 客户端配置
- 实现推理 API 调用
- 实现审核队列 API 调用
- 实现统计 API 调用

#### 步骤 7: 创建通用组件
- 创建图片查看器组件
- 创建边界框绘制组件
- 创建加载状态组件
- 创建错误提示组件

#### 步骤 8: 样式和响应式设计
- 配置 Ant Design 主题
- 实现响应式布局
- 优化移动端体验

### 页面设计

#### 首页 (/)
- 系统介绍
- 快速导航
- 系统状态

#### 推理页面 (/inference)
- 图片上传区域
- 推理结果展示
- 检测框可视化
- 决策结果展示

#### 审核页面 (/review)
- 审核队列列表
- 图片预览
- 标注编辑器
- 审核操作按钮
- 分页控制

#### 统计页面 (/stats)
- 总体统计卡片
- 决策统计图表
- 审核统计图表
- 详细数据表格

### 组件结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── Inference/
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── ResultDisplay.tsx
│   │   │   └── BoundingBox.tsx
│   │   ├── Review/
│   │   │   ├── QueueList.tsx
│   │   │   ├── ImagePreview.tsx
│   │   │   ├── AnnotationEditor.tsx
│   │   │   └── ReviewActions.tsx
│   │   ├── Stats/
│   │   │   ├── StatCard.tsx
│   │   │   ├── DecisionChart.tsx
│   │   │   └── ReviewChart.tsx
│   │   └── Common/
│   │       ├── Loading.tsx
│   │       └── Error.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Inference.tsx
│   │   ├── Review.tsx
│   │   └── Stats.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

### API 接口定义

```typescript
interface Detection {
  cls: string;
  conf: number;
  bbox: [number, number, number, number];
}

interface Decision {
  action: 'auto_accept' | 'send_to_review' | 'discard';
  confidence: number;
}

interface InferenceResponse {
  success: boolean;
  data?: {
    image_path: string;
    detections: Detection[];
    decisions: Decision[];
  };
  message?: string;
}

interface ReviewQueueItem {
  sample_id: number;
  image_path: string;
  detection_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  decision_action: string;
}

interface ReviewRequest {
  reviewer: string;
  action: 'accepted' | 'rejected' | 'modified';
  modified_bbox?: { x: number; y: number; w: number; h: number };
}

interface Statistics {
  total_samples: number;
  total_detections: number;
  decision_stats: {
    auto_accept: number;
    send_to_review: number;
    discard: number;
  };
  review_stats: {
    accepted: number;
    rejected: number;
    modified: number;
  };
}
```

### 预期结果
- React 前端项目可以正常启动
- 推理页面能够上传图片并显示检测结果
- 审核页面能够显示审核队列并进行标注编辑
- 统计页面能够显示系统统计信息
- 所有页面具有良好的用户体验和响应式设计

### 注意事项
- 使用 TypeScript 确保类型安全
- 使用 Ant Design 组件库提高开发效率
- 实现良好的错误处理和用户提示
- 优化图片加载和渲染性能
- 确保跨域请求正常工作
- 实现适当的加载状态和错误提示
