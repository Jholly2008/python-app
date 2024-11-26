#!/bin/bash

# 默认值
DEFAULT_VERSION="1.0"

# 显示使用方法
usage() {
   echo "Usage: $0 [version]"
   echo "Default version: $DEFAULT_VERSION"
   echo "Example: $0 1.0"
}

# 获取参数，使用默认值
VERSION=${1:-$DEFAULT_VERSION}

# 容器配置
CONTAINER_NAME="service-b"
IMAGE_NAME="kkk2099/kkk"
SERVICE_NAME="service-b"
PORT="10002"

# 检查并移除已存在的容器
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
   echo "Stopping and removing existing container..."
   docker stop $CONTAINER_NAME
   docker rm $CONTAINER_NAME
fi

# 运行新容器
echo "Starting $SERVICE_NAME..."
echo "Version: $VERSION"

docker run -d \
   -p $PORT:$PORT \
   -e APP_VERSION=$VERSION \
   --name $CONTAINER_NAME \
   $IMAGE_NAME:$SERVICE_NAME-$VERSION

echo "Container started. Use 'docker logs $CONTAINER_NAME' to view logs."