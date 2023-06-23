import re
import typing
from typing import Any
from pydantic import BaseModel


class Property(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class Parameters(BaseModel):
    type: str = "object"
    properties: list[Property]


class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters
    func: typing.Callable

    @classmethod
    def load_from_func(cls, func: typing.Callable) -> typing.Self:
        typing_map = {
            int: "number",
            str: "string",
            bool: "boolean",
            dict: "object",
            list: "array",
        }
        doc_string = func.__doc__
        if not doc_string:
            raise AttributeError("Function has no docstring")

        main_doc = doc_string.split(":param", 1)[0].strip()

        properties = re.findall(r":param\s+(.+):\s+(.+)", doc_string, re.MULTILINE)

        property_dict: dict[str, Property] = {}
        for name, description in properties:
            property_dict[name] = Property(
                name=name, type="", description=description, required=True
            )

        for name, type_cls in func.__annotations__.items():
            if name in property_dict:
                property_dict[name].type = typing_map.get(type_cls, "object")

        properties = [property for property in property_dict.values() if property.type]

        return cls(
            name=func.__name__,
            description=main_doc,
            parameters=Parameters(properties=properties),
            func=func,
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.func(*args, **kwds)

    def to_params(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": self.parameters.type,
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description,
                    }
                    for p in self.parameters.properties
                },
                "required": [p.name for p in self.parameters.properties if p.required],
            },
        }
