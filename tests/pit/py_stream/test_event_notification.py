import json
from unittest.mock import MagicMock

import pytest

from pit.py_stream.event_notification import EventPubSubNotification
from pit.py_stream.settings import EventConfig


@pytest.fixture
def pubsub_client():
    return MagicMock()


@pytest.fixture
def event_config():
    return EventConfig(bindings={"my-topic": "job-created"})


@pytest.fixture
def event_notification(pubsub_client, event_config):
    project_name = "my-project"
    return EventPubSubNotification(pubsub_client, project_name, event_config)


def test_notify_with_string_message(pubsub_client, event_notification):
    # Arrange
    topic = "my-topic"
    message = "Hello, world!"
    headers = {"header1": "value1", "header2": "value2"}

    # Act
    event_notification.notify(topic, message, headers)

    # Assert
    topic_path = pubsub_client.topic_path.return_value
    pubsub_client.publish.assert_called_once_with(
        topic_path, message.encode("utf-8"), **headers
    )


def test_notify_with_string_message_no_headers(pubsub_client, event_notification):
    # Arrange
    topic = "my-topic"
    message = "Hello, world!"

    # Act
    event_notification.notify(topic, message)

    # Assert
    topic_path = pubsub_client.topic_path.return_value
    pubsub_client.publish.assert_called_once_with(
        topic_path, message.encode("utf-8")
    )


def test_notify_with_dict_message(pubsub_client, event_notification):
    # Arrange
    topic = "my-topic"
    message = {"key": "value"}
    headers = {"header1": "value1", "header2": "value2"}

    # Act
    event_notification.notify(topic, message, headers)

    # Assert
    topic_path = pubsub_client.topic_path.return_value
    message_str = json.dumps(message, default=str)
    pubsub_client.publish.assert_called_once_with(
        topic_path, message_str.encode("utf-8"), **headers
    )


def test_topic_not_exists__rise_error(
        pubsub_client, event_notification: EventPubSubNotification
):
    # Arrange
    topic = "my-topic"
    message = "Hello, world!"
    headers = {"header1": "value1", "header2": "value2"}

    pubsub_client.publish.side_effect = RuntimeError("Topic not found")

    with pytest.raises(RuntimeError, match="Topic not found"):
        event_notification.notify(topic, message, headers)
