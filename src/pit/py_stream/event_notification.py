import abc
import json
import logging
from dataclasses import dataclass

from pit.py_stream.settings import EventConfig
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)


class EventNotification(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def notify(self, binding: str, message: dict | str, headers: dict = None):
        raise NotImplementedError


@dataclass(repr=False, eq=False)
class EventPubSubNotification(EventNotification):
    client: pubsub_v1.PublisherClient
    project_name: str
    event_config: EventConfig

    def notify(self, binding: str, message: dict | str, headers: dict = None):
        logger.debug("Notify [%s] => [%s]", message, binding)
        topic = self.event_config.bindings.get(binding)
        topic_path = self.client.topic_path(self.project_name, topic)

        message_str = (
            message if isinstance(message, str) else json.dumps(message, default=str)
        )

        data = message_str.encode("utf-8")

        if headers is not None:
            self.client.publish(topic_path, data, **headers)
        else:
            self.client.publish(topic_path, data)
