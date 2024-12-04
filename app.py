import time
import os

from flask import Flask, request, jsonify
from instagram_handler import setup_instagram_routes

app = Flask(__name__)

APP_VERSION = os.getenv('APP_VERSION', '1.0.0')


# 添加睡眠时间配置
class Config:
    SLEEP_TIME = 0  # 默认睡眠时间为0秒


@app.route('/api/set_sleep_time', methods=['POST'])
def set_sleep_time():
    data = request.get_json()
    new_sleep_time = data.get('sleep_time')

    if new_sleep_time is None:
        return jsonify({'error': 'sleep_time is required'}), 400

    try:
        new_sleep_time = float(new_sleep_time)
        if new_sleep_time < 0:
            return jsonify({'error': 'sleep_time must be non-negative'}), 400

        Config.SLEEP_TIME = new_sleep_time
        return jsonify({
            'message': 'Sleep time updated successfully',
            'sleep_time': new_sleep_time
        }), 200
    except ValueError:
        return jsonify({'error': 'sleep_time must be a valid number'}), 400


import uuid


def get_span_id(request):
    """获取或生成span id"""
    is_kubernetes = os.getenv('APP_KUBERNETES_ENABLED', 'false').lower() == 'true'

    if is_kubernetes:
        span_id = request.headers.get('X-B3-SpanId')
        if span_id:
            app.logger.debug("Using Istio generated spanId: %s", span_id)
            return span_id
        else:
            app.logger.warning("No spanId found in k8s environment")
            return ""
    else:
        new_span_id = "service-b-" + uuid.uuid4().hex[:16]
        app.logger.debug("Generated new spanId in non-k8s environment: %s", new_span_id)
        return new_span_id


@app.route('/api/cost', methods=['GET'])
def cost():
    # 打印所有请求头
    print("\n=== All Request Headers ===")
    for header_name, header_value in request.headers:
        print(f"{header_name}: {header_value}")

    # 特别打印 baggage 相关信息
    print("\n=== Baggage Header ===")
    print(f"baggage: {request.headers.get('baggage', 'Not Found')}")

    # 获取 B3 headers
    trace_id = request.headers.get('X-B3-TraceId', '')
    parent_span_id = request.headers.get('X-B3-SpanId', '')
    span_id = get_span_id(request)

    start_time = int(time.time() * 1000)
    time.sleep(Config.SLEEP_TIME)
    end_time = int(time.time() * 1000)

    # 包含完整请求头信息在 trace_info 中
    headers_dict = dict(request.headers)

    trace_info = {
        "traceId": trace_id,
        "spanId": span_id,
        "parentSpanId": parent_span_id,
        "serviceName": "serviceB",
        "version": APP_VERSION,
        "startTime": start_time,
        "endTime": end_time,
        "costTime": end_time - start_time,
        "requestBody": str(request.headers.to_wsgi_list()),
        "responseBody": {
            "message": "Test successful",
            "config_time": Config.SLEEP_TIME
        }
    }

    response = jsonify({
        "message": "Test successful",
        "config_time": Config.SLEEP_TIME,
        "trace_info": trace_info
    })

    response.headers['X-B3-TraceId'] = trace_id
    response.headers['X-B3-SpanId'] = span_id
    response.headers['X-B3-ParentSpanId'] = parent_span_id

    return response, 200


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'}), 200


# 注册Instagram相关路由
setup_instagram_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10002)
