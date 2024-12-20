import instaloader
from flask import request, jsonify

# 初始化Instaloader
loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)
USER = "kkkggg3001"
PASSWORD = "13579@Kxj"
loader.login(USER, PASSWORD)
print(f"Logged in successfully as {USER}")

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


def setup_instagram_routes(app):
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

    @app.route('/get_media_urls', methods=['POST'])
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

            images = []
            videos = []

            if post.typename == 'GraphSidecar':
                # Handle multiple media items
                for node in post.get_sidecar_nodes():
                    if node.is_video:
                        videos.append(node.video_url)
                    else:
                        images.append(node.display_url)
            else:
                # Handle single media item
                if post.is_video:
                    videos.append(post.video_url)
                elif post.url:
                    images.append(post.url)

            response_data = {
                "errcode": 0,
                "images": images,
                "videos": videos
            }

            return jsonify(response_data), 200
        except Exception as e:
            return jsonify({'errcode': 1, 'errmsg': str(e)}), 500