#!/bin/bash

echo "========================================"
echo "YOLO标注代理系统 - 部署脚本"
echo "========================================"
echo ""

echo "[1/5] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi
echo "✓ Python环境检查通过"
echo ""

echo "[2/5] 创建虚拟环境..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ 虚拟环境创建成功"
else
    echo "✓ 虚拟环境已存在"
fi
echo ""

echo "[3/5] 激活虚拟环境并安装依赖..."
source .venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi
echo "✓ 依赖安装完成"
echo ""

echo "[4/5] 创建必要的目录..."
mkdir -p data/temp
mkdir -p logs
mkdir -p models
echo "✓ 目录创建完成"
echo ""

echo "[5/5] 检查模型文件..."
if [ ! -f "models/best.pt" ]; then
    echo "警告: 未找到 models/best.pt"
    echo "请将训练好的YOLO模型文件放置在 models/ 目录下"
else
    echo "✓ 模型文件检查通过"
fi
echo ""

echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "使用方法:"
echo "1. 运行批量推理: python run_batch_inference.py"
echo "2. 启动API服务器: python run_api.py"
echo "3. 打开Web界面: 在浏览器中打开 frontend/index.html"
echo ""
