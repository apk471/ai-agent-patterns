from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from typing import Any, get_args, get_origin


def _annotation_to_schema(annotation: Any) -> dict[str, Any]:
    if annotation is inspect._empty:
        return {"type": "str"}

    origin = get_origin(annotation)
    if origin is None:
        if annotation is str:
            return {"type": "str"}
        if annotation is int:
            return {"type": "int"}
        if annotation is float:
            return {"type": "float"}
        if annotation is bool:
            return {"type": "bool"}
        return {"type": getattr(annotation, "__name__", "str")}

    args = [arg for arg in get_args(annotation) if arg is not type(None)]
    if len(args) == 1:
        return _annotation_to_schema(args[0])
    return {"type": "str"}


@dataclass
class Tool:
    name: str
    description: str
    fn: Any
    fn_signature: str

    def run(self, **kwargs: Any) -> Any:
        return self.fn(**kwargs)


def tool(fn: Any) -> Tool:
    signature = inspect.signature(fn)
    properties: dict[str, dict[str, Any]] = {}
    required: list[str] = []

    for name, parameter in signature.parameters.items():
        schema = _annotation_to_schema(parameter.annotation)
        if parameter.default is inspect._empty:
            required.append(name)
        else:
            schema["default"] = parameter.default
        properties[name] = schema

    description = inspect.getdoc(fn) or f"Tool for {fn.__name__}"
    fn_signature = json.dumps(
        {
            "name": fn.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
    )

    return Tool(
        name=fn.__name__,
        description=description,
        fn=fn,
        fn_signature=fn_signature,
    )
