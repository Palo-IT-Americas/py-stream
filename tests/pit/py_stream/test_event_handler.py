from unittest.mock import Mock

from google.cloud import pubsub_v1
from pytest import fixture

from pit.py_stream.event_handler import EventRouter, PubSubEventHandler
from pit.py_stream.settings import EventConfig


@fixture
def router() -> EventRouter:
    router = EventRouter()

    @router.event("tes_event")
    def test_event(event):
        pass

    return router


@fixture
def pubsub_event_config() -> EventConfig:
    return EventConfig(bindings={"test_event": "test_event"})


@fixture
def pub_sub_event_handler(router, pubsub_event_config) -> PubSubEventHandler:
    return PubSubEventHandler(
        subscriber=Mock(spec_set=pubsub_v1.SubscriberClient),
        publisher=Mock(spec_set=pubsub_v1.PublisherClient),
        project_name="test_project",
        event_config=pubsub_event_config,
    )


def test_add_router(pub_sub_event_handler, router):
    # Act
    pub_sub_event_handler.add_router(router)

    # Assert
    assert router in pub_sub_event_handler.routers


def test_start_listening(pub_sub_event_handler, router):
    # Arrange
    pub_sub_event_handler.add_router(router)

    # Act
    pub_sub_event_handler.start_listening()

    # Assert
    pub_sub_event_handler.subscriber.subscribe.assert_called_once()
    pub_sub_event_handler.subscriber.subscription_path.assert_called_once()
    pub_sub_event_handler.subscriber.get_subscription.assert_called_once()


def test_start_listening_subscription_not_exist(pub_sub_event_handler, router):
    # Arrange
    pub_sub_event_handler.add_router(router)
    pub_sub_event_handler.subscriber.get_subscription.side_effect = Exception

    # Act
    pub_sub_event_handler.start_listening()

    # Assert
    pub_sub_event_handler.subscriber.subscribe.assert_not_called()
