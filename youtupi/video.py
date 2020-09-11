class Video:
    def __init__(self, vid, data, url = None, subtitles = None):
        self.vid = vid
        self.data = data
        self.url = url
        self.subtitles = subtitles
        self.played = False