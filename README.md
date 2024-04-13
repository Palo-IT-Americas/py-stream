# py-stream

A Python library that provides a common interface to different message brokers such as PubSub, Kafka, RabbitMQ. It abstracts the complexity of using these brokers' APIs directly, allowing developers to focus on their application logic. 

**Currently, in version 1.0.0, only PubSub is supported.** The library includes features like EventRouter and EventNotification for efficient message routing and notification.

## Features

- **Abstraction over different brokers**: This library provides a common interface to different brokers such as PubSub, Kafka, RabbitMQ. This abstraction simplifies the complexity of using the APIs of these brokers directly.
- **EventRouter**: It allows you to decorate functions that will work as consumers.
- **EventNotification.notify**: It publishes an event by looking up the topic name within `EventConfig.bindings[str,str]`.
- **Topic name abstraction**: The reason for not using the topic name directly in the code and using `EventConfig.bindings` is to allow changing the topic name without altering the code. The real name is the value of the dictionary `EventConfig.bindings`.

## Quick Start

1. Install the library using pip:
```bash
poetry install
```
2. Import the necessary classes from the library:
```python
from py_stream.event_notification import EventNotification
from py_stream.settings import EventConfig
```
3. Create an instance of `EventConfig` with your topic bindings:
```python
event_config = EventConfig(bindings={"my-topic-alias": "job-created"})
```
4. Create an instance of `EventNotification` with your PubSub client, project name, and event config:
```python
event_notification = EventPubSubNotification(pubsub_client, "gcp-project-name", event_config)
```
5. Now you can use `event_notification.notify("my-topic-alias", { "name":"Dave","last_name":"Jhones" })` to publish messages to your topic.

## Usage

To use this library, you need to create an instance of `EventNotification` and `EventConfig`. `EventConfig` holds the bindings for your topics. These bindings allow you to change the topic name without altering the code.

Here is an example of how to publish an event:

```python
from py_stream.event_notification import EventPubSubNotification
from py_stream.settings import EventConfig
from google.cloud import pubsub_v1

# Create an instance of EventConfig with your topic bindings
event_config = EventConfig(bindings={"my-topic-alias": "real.topic.name"})

# Create an instance of EventNotification with your PubSub client, project name, and event config
event_notification = EventPubSubNotification(pubsub_v1.PublisherClient(), "gcp-project-name", event_config)

# Now you can use event_notification.notify() to publish messages to your topic
event_notification.notify("my-topic", { "name":"Dave","last_name":"Jhones" })
```

Here is an example of how to consume an event:

```python
from google.cloud import pubsub_v1

from py_stream.event_handler import EventRouter, PubSubEventHandler
from py_stream.settings import EventConfig

# Create an instance of EventConfig with your topic bindings
event_config = EventConfig(bindings={"my-subscription-alias": "real-subscription-name"})
event_router = EventRouter()


# Decorate your function with event_router.subscribe() to consume messages from your topic
@event_router.event("my-subscription-alias")
def my_function(data):
    print(data)


event_handler:PubSubEventHandler = PubSubEventHandler(
    pubsub_v1.SubscriberClient(), 
    pubsub_v1.PublisherClient(),
    "gcp-project-name", 
    event_config)
   
event_handler.add_router(event_router)
# Start the event router
event_handler.start_listening()

while True:
    pass
```

## Notes
- Event Handler needs something to keep running the script to keep listening to the messages. In the example above, we used a `while True: pass` loop. In a real application, you might want to use a more sophisticated mechanism to keep the script running.
- The `EventRouter` class is responsible for routing messages to the correct function. It uses the `EventConfig` class to look up the subscription name.
- This library is compatible to FastAPI, is recommended start the PubSubEventHandler inside the lifespan function. See [Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)