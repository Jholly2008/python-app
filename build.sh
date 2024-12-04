#!/bin/bash

# 设置变量
DOCKER_IMAGE_NAME="kkk2099/kkk:service-b-1.0"

echo "开始构建Python服务..."

# 找到并停止和删除所有基于指定镜像的容器
CONTAINER_IDS=$(docker ps -a -q --filter ancestor="$DOCKER_IMAGE_NAME")

if [ -n "$CONTAINER_IDS" ]; then
    echo "找到容器，ID: $CONTAINER_IDS。"

    # 停止所有找到的容器
    echo "正在停止容器..."
    docker stop $CONTAINER_IDS

    # 检查停止容器是否成功
    if [ $? -ne 0 ]; then
        echo "停止容器失败，脚本终止。"
        exit 1
    fi

    # 删除所有找到的容器
    echo "正在删除容器..."
    docker rm $CONTAINER_IDS

    # 检查删除容器是否成功
    if [ $? -ne 0 ]; then
        echo "删除容器失败，脚本终止。"
        exit 1
    fi
else
    echo "未找到相关的容器。"
fi

# 找到Docker镜像的imageId
IMAGE_ID=$(docker images -q "$DOCKER_IMAGE_NAME")

# 删除旧的Docker镜像
if [ -n "$IMAGE_ID" ]; then
    echo "正在删除旧的Docker镜像..."
    docker rmi "$IMAGE_ID"
    # 检查镜像删除是否成功
    if [ $? -ne 0 ]; then
        echo "删除旧的Docker镜像失败，脚本终止。"
        exit 1
    fi
else
    echo "未找到旧的Docker镜像。"
fi

# 构建新的Docker镜像
echo "正在构建新的Docker镜像..."
docker build -t "$DOCKER_IMAGE_NAME" .

# 检查Docker构建是否成功
if [ $? -ne 0 ]; then
    echo "Docker镜像构建失败。"
    exit 1
fi

echo "Docker镜像构建成功: $DOCKER_IMAGE_NAME"

# 询问是否要推送到DockerHub
read -p "是否要推送镜像到DockerHub？(y/n): " PUSH_CHOICE

if [ "$PUSH_CHOICE" = "y" ] || [ "$PUSH_CHOICE" = "Y" ]; then
    echo "正在推送镜像到DockerHub..."
    docker push "$DOCKER_IMAGE_NAME"

    # 检查推送是否成功
    if [ $? -ne 0 ]; then
        echo "推送到DockerHub失败。"
        exit 1
    else
        echo "推送到DockerHub成功。"
    fi
else
    echo "跳过推送到DockerHub。"
fi

echo "脚本执行完成。"
