import logging
import time

logger = logging.getLogger(__name__)


class EventConsumer(object):
    def __init__(self, streams, group, consumer_name, db, event_cls, consume_from_end=False):
        """
        An event consumer

        :param streams: List of stream names
        :param group: The name of this consumer group
        :param consumer_name: The name of this consumer
        :param db: A walrus DB object
        :param event_cls: A protobuf class from .events
        :param consume_from_end: skip old events
        """
        self.db = db
        self.cg = self.db.consumer_group(group, streams, consumer_name)
        self.cg.create(mkstream=True)
        self.stop = False
        self.event_cls = event_cls

        if consume_from_end:
            self.cg.set_id('$')

    def get_events(self, count=1, block=0):
        resp = self.cg.read(count, block)

        if resp:
            for stream, events in resp:
                stream = stream.decode('utf-8')
                for event_id, event in events:
                    event_id = event_id.decode('utf-8')
                    yield self.event_cls.FromString(event)

    def iter_events(self, count=10, block=None, sleep=0.1):
        while True:
            if self.stop:
                break

            num_events = 0
            for event in self.get_events(count=count, block=block):
                yield event
                num_events += 1

            if not num_events:
                time.sleep(sleep)
