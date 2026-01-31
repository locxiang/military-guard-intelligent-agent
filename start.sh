#!/bin/bash

# 保卫核心业务智能体 - 快速启动脚本

echo "=========================================="
echo "  保卫核心业务智能体 - 开发环境启动"
echo "=========================================="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: docker-compose未安装"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env文件不存在，从.env.example复制..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ 已创建.env文件，请根据需要修改配置"
    else
        echo "❌ 错误: .env.example文件不存在"
        exit 1
    fi
fi

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/{mysql,uploads,logs,backups}

# 启动服务
echo "🚀 启动Docker服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ 服务启动完成！"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  MySQL: localhost:3306"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo "=========================================="
