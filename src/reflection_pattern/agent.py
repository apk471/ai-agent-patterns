from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_GENERATION_SYSTEM_PROMPT = (
    "You are a Python programmer tasked with generating high quality Python code. "
    "Your task is to generate the best content possible for the user's request. "
    "If the user provides critique, respond with a revised version of your previous attempt."
)
DEFAULT_REFLECTION_SYSTEM_PROMPT = (
    "You are a python developer, an experienced computer scientist. "
    "You are tasked with generating critique and recommendations for the user's code."
)

logger = logging.getLogger("reflection_pattern.agent")


@dataclass
class ReflectionAgent:
    """Implementation of the reflection pattern with generator + critic loops."""

    model: str = DEFAULT_MODEL
    client: Optional[Groq] = None
    max_completion_tokens: int = 600
    max_message_chars: int = 3500
    keep_recent_generation_messages: int = 6

    def __post_init__(self) -> None:
        load_dotenv()
        self.client = self.client or Groq(api_key=os.getenv("GROQ_API_KEY"))

    def run(
        self,
        user_msg: str,
        generation_system_prompt: str = DEFAULT_GENERATION_SYSTEM_PROMPT,
        reflection_system_prompt: str = DEFAULT_REFLECTION_SYSTEM_PROMPT,
        n_steps: int = 10,
        verbose: int = 0,
    ) -> str:
        """Run alternating generation/reflection for n steps and return final output."""
        if n_steps < 1:
            raise ValueError("n_steps must be at least 1")
        logger.info("Starting reflection agent run (model=%s, steps=%s)", self.model, n_steps)

        generation_chat_history = [{"role": "system", "content": generation_system_prompt}]
        generation_chat_history.append({"role": "user", "content": self._clip_text(user_msg)})
        logger.debug("Initial user prompt: %s", user_msg)

        answer = self._complete(self._prune_generation_history(generation_chat_history))
        generation_chat_history.append({"role": "assistant", "content": answer})

        if verbose:
            logger.info("Generation step 0 output:\n%s", answer)

        for step in range(1, n_steps):
            reflection_chat_history = [{"role": "system", "content": reflection_system_prompt}]
            reflection_chat_history.append({"role": "user", "content": self._clip_text(answer)})

            critique = self._complete(reflection_chat_history)
            if verbose:
                logger.info("Reflection step %s critique:\n%s", step, critique)

            generation_chat_history.append({"role": "user", "content": self._clip_text(critique)})
            answer = self._complete(self._prune_generation_history(generation_chat_history))
            generation_chat_history.append({"role": "assistant", "content": answer})

            if verbose:
                logger.info("Generation step %s output:\n%s", step, answer)

        logger.info("Reflection agent run completed")
        return answer

    def _complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            max_completion_tokens=self.max_completion_tokens,
        )
        content = response.choices[0].message.content
        return content or ""

    def _clip_text(self, text: str) -> str:
        if len(text) <= self.max_message_chars:
            return text
        clipped = text[: self.max_message_chars]
        logger.debug(
            "Clipped message from %s chars to %s chars", len(text), len(clipped)
        )
        return clipped

    def _prune_generation_history(
        self, messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Keep system prompt plus the most recent turns to avoid oversized requests."""
        if len(messages) <= 1:
            return messages
        system_message = messages[0]
        tail = messages[1:][-self.keep_recent_generation_messages :]
        return [system_message, *tail]
