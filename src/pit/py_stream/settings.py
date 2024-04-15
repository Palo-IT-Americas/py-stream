from typing import Literal

from pydantic import BaseModel, Field


class EventPubSubConfig(BaseModel):
    project_name: str = Field(default="proj", description="GCP Project Name")


class EventConfig(BaseModel):
    type: Literal["pubsub"] = Field(description="Messaging provider", default="pubsub")
    pubsub: EventPubSubConfig | None = None
    bindings: dict[str, str] = Field(
        description="Map(str,str), key is the binding name used in code to be an alias of a topic or subscription,"
                    "this is used to get the name of the topic or subscription contained in the value",
        default={},
    )
