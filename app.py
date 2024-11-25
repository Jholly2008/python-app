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


def check_authorization():
    """检查Authorization头部是否包含有效的Token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    # 检查是否以"Bearer "开头，并且Token是否匹配
    token = auth_header.split(" ")[1] if " " in auth_header else None
    return token == AUTH_TOKEN


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
    app.run(host='0.0.0.0', port=29001)
