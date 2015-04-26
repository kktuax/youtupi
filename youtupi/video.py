class Video:
    def __init__(self, vid, data, url = None, subs = None):
        self.vid = vid
        self.data = data
        self.url = url
        self.subs = subs
        self.played = False