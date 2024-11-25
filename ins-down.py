import instaloader

loader = instaloader.Instaloader(
    download_comments=True,
    download_geotags=True,
    download_pictures=True,
    download_video_thumbnails=True,
    save_metadata=True
)
USER = "xiangjunkong90"
PASSWORD = "13579@insKxj"
loader.login(USER, PASSWORD)
url = 'https://www.instagram.com/reel/DBTsK6eymUC/?igsh=d2tmamZ4bmNua3Bu'
shortcode = url.split('/')[-2]
try:
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    photo_url = post.url  # this will be post's thumbnail (or first slide)
    video_url = post.video_url  # if post.is_video is True then it will be url of video file
    print(photo_url)
    print(video_url)
    # target is the folder name where it's going to be saved
    # loader.download_post(post, target=shortcode)
except Exception as e:
    print(f'Something went wrong: {e}')
