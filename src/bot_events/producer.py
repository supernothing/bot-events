class EventProducer(object):
    def __init__(self, stream, db, max_len=None):
        """
        An event producer

        :param stream: Stream name
        :param db: Walrus db object
        """
        self.db = db
        self.stream = self.db.Stream(stream)
        self.max_len = max_len

    def add_event(self, event):
        self.stream.add({'event': event.SerializeToString()}, maxlen=self.max_len)
