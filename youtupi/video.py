class Video:
    def __init__(self, vid, data, url = None):
        self.vid = vid
        self.data = data
        self.url = url
        self.played = False