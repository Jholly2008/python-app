import time
import os

from flask import Flask, request, jsonify
import instaloader

app = Flask(__name__)

# 初始化Instaloader
loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)

# TODO 暂时授权Token是一个固定的字符串
AUTH_TOKEN = "YourSecretTokenWithKong"
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')


def check_authorization():
    """检查Authorization头部是否包含有效的Token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    # 检查是否以"Bearer "开头，并且Token是否匹配
    token = auth_header.split(" ")[1] if " " in auth_header else None
    return token == AUTH_TOKEN


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


def generate_span_id():
    """生成16位的span id"""
    return uuid.uuid4().hex[:16]


@app.route('/api/cost', methods=['GET'])
def cost():
    # 获取 B3 headers
    trace_id = request.headers.get('X-B3-TraceId', '')
    # 从请求头中的 X-B3-SpanId 作为 parentSpanId
    parent_span_id = request.headers.get('X-B3-SpanId', '')
    # 为当前服务生成新的 spanId
    span_id = "service-b-" + generate_span_id()

    start_time = int(time.time() * 1000)

    time.sleep(Config.SLEEP_TIME)

    end_time = int(time.time() * 1000)

    trace_info = {
        "traceId": trace_id,
        "spanId": span_id,  # 使用新生成的spanId
        "parentSpanId": parent_span_id,  # 使用请求中的X-B3-SpanId作为parentSpanId
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

    # 在响应头中设置新的spanId，以便下游服务使用
    response.headers['X-B3-TraceId'] = trace_id
    response.headers['X-B3-SpanId'] = span_id
    response.headers['X-B3-ParentSpanId'] = parent_span_id

    return response, 200


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'}), 200


@app.route('/download', methods=['POST'])
def download_instagram_post():
    if not check_authorization():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    shortcode = url.split('/')[-2]

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)
        return jsonify({'message': f'Downloaded post {shortcode} successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_media_urls', methods=['GET'])
def get_media_urls():
    if not check_authorization():
        return jsonify({'errcode': 1, 'errmsg': 'Unauthorized'}), 401

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'errcode': 1, 'errmsg': 'URL is required'}), 400

    shortcode = url.split('/')[-2]
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # 获取图片和视频的URL
        image_url = post.url if post.url else None
        video_url = post.video_url if post.is_video else None

        response_data = {
            "errcode": 0,
            "images": [image_url] if image_url else [],
            "videos": [video_url] if video_url else []
        }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'errcode': 1, 'errmsg': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10002)
