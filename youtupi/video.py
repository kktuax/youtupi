class Video:
    def __init__(self, vid, data, url):
        self.vid = vid
        self.data = data
        self.url = url
        self.played = False

def createVideo(data):
    from youtupi.modules import youtube
    try:
        return youtube.createVideo(data)
    except Exception: 
        url = data['id']
        return Video(data['id'], data, url)