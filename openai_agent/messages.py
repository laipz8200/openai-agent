import json
from pydantic import BaseModel


class Message(BaseModel):
    content: str
    role: str

    def to_params(self) -> dict:
        return {"content": self.content or "", "role": self.role}


class SystemMessage(Message):
    role: str = "system"


class UserMessage(Message):
    role: str = "user"


class AssistantMessage(Message):
    role: str = "assistant"


class FunctionMessage(Message):
    role: str = "function"
    name: str

    def to_params(self) -> dict:
        dictionary = super().to_params()
        dictionary.update({"name": self.name})
        return dictionary


class FunctionCall(BaseModel):
    name: str
    arguments: str

    def args_to_json(self) -> dict:
        return json.loads(self.arguments)


class FunctionCallMessage(Message):
    function_call: FunctionCall
    content: None = None
