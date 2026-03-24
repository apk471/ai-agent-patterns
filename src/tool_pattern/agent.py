from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from dotenv import load_dotenv
from groq import Groq

from .tool import Tool

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_TOOL_SYSTEM_PROMPT = """
You are a helpful AI assistant with access to tools.
Decide whether a tool is needed to answer the user's request.

If a tool is needed, respond with exactly one tool call inside <tool_call></tool_call> tags:
<tool_call>
{"name": "<tool-name>", "arguments": {"arg": "value"}}
</tool_call>

If no tool is needed, respond with the final answer inside <final_answer></final_answer> tags:
<final_answer>
Your answer here
</final_answer>

Only call a tool when it is actually useful. Do not invent arguments.
If the user does not specify a unit for weather, omit the unit argument so the tool can return both Celsius and Fahrenheit.

Available tools:
<tools>
{tool_signatures}
</tools>
""".strip()


@dataclass
class ToolAgent:
    tools: list[Tool]
    model: str = DEFAULT_MODEL
    client: Optional[Groq] = None
    max_completion_tokens: int = 600
    system_prompt_template: str = DEFAULT_TOOL_SYSTEM_PROMPT
    tools_by_name: dict[str, Tool] = field(init=False)

    def __post_init__(self) -> None:
        load_dotenv()
        self.client = self.client or Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.tools_by_name = {tool.name: tool for tool in self.tools}

    def run(self, user_msg: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self.system_prompt_template.format(
                    tool_signatures=self._tool_signatures()
                ),
            },
            {"role": "user", "content": user_msg},
        ]

        first_response = self._complete(messages)
        tool_call = self._extract_tag_content(first_response, "tool_call")
        if not tool_call:
            final_answer = self._extract_tag_content(first_response, "final_answer")
            return final_answer or first_response

        call = json.loads(tool_call)
        tool_name = call["name"]
        arguments = call.get("arguments", {})

        if tool_name not in self.tools_by_name:
            raise ValueError(f"Unknown tool requested by model: {tool_name}")

        result = self.tools_by_name[tool_name].run(**arguments)
        follow_up_messages = [
            {"role": "system", "content": "Answer the user's request using the tool result."},
            {"role": "user", "content": user_msg},
            {
                "role": "assistant",
                "content": f"Tool used: {tool_name}\nArguments: {json.dumps(arguments)}",
            },
            {"role": "user", "content": f"Tool result: {self._stringify_result(result)}"},
        ]
        final_response = self._complete(follow_up_messages)
        extracted_final = self._extract_tag_content(final_response, "final_answer")
        return extracted_final or final_response

    def _complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            max_completion_tokens=self.max_completion_tokens,
        )
        return response.choices[0].message.content or ""

    def _tool_signatures(self) -> str:
        return json.dumps(
            [json.loads(tool.fn_signature) for tool in self.tools],
            indent=2,
        )

    @staticmethod
    def _stringify_result(result: Any) -> str:
        if isinstance(result, str):
            return result
        return json.dumps(result)

    @staticmethod
    def _extract_tag_content(text: str, tag: str) -> str:
        pattern = rf"<{tag}>\s*(.*?)\s*</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
