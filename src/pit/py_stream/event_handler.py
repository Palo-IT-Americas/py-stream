import logging
from dataclasses import dataclass, field

from google.cloud import pubsub_v1

from pit.py_stream.settings import EventConfig

logger = logging.getLogger(__name__)


class EventRouter:
    def __init__(self):
        self.callbacks = {}

    def event(self, binding: str):
        def decorator(func):
            self.callbacks[binding] = func
            return func

        return decorator


@dataclass(repr=False, eq=False)
class PubSubEventHandler:

    subscriber: pubsub_v1.SubscriberClient
    publisher: pubsub_v1.PublisherClient
    project_name: str
    event_config: EventConfig
    routers: list = field(init=False, default_factory=list)

    def add_router(self, router: EventRouter):
        self.routers.append(router)

    def start_listening(self):
        for router in self.routers:
            for binding, callback in router.callbacks.items():

                subscription_name = self.event_config.bindings.get(binding)

                subscription_path = self.subscriber.subscription_path(
                    self.project_name, subscription_name
                )

                subscription_exist = self._is_subscription_exist(subscription_path)
                if subscription_exist:
                    self.subscriber.subscribe(subscription_path, callback=callback)
                else:
                    name = getattr(callback, "__name__", repr(callback))
                    logger.error(
                        "The subscription [%s] does not exist, the callback [%s] will not be executed",
                        subscription_name,
                        name,
                    )

    def _is_subscription_exist(self, subscription_path):
        try:
            self.subscriber.get_subscription(
                request={"subscription": subscription_path}
            )
            return True
        except Exception as e:
            logger.warning(
                "The subscription [%s] does not exist, reason: [%s]",
                subscription_path,
                str(e),
            )
            return False
