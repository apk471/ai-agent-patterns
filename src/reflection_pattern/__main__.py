import argparse

from .agent import (
    DEFAULT_GENERATION_SYSTEM_PROMPT,
    DEFAULT_MODEL,
    DEFAULT_REFLECTION_SYSTEM_PROMPT,
    ReflectionAgent,
)
from .logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the reflection pattern agent")
    parser.add_argument("prompt", help="User prompt for the generation step")
    parser.add_argument("--steps", type=int, default=5, help="Number of reflection iterations")
    parser.add_argument(
        "--model",
        default=None,
        help="Groq model id (for example: openai/gpt-oss-20b)",
    )
    parser.add_argument("--verbose", type=int, default=1, help="Print intermediate generations and critiques")
    parser.add_argument(
        "--max-completion-tokens",
        type=int,
        default=600,
        help="Hard cap for each model completion to reduce token usage",
    )
    parser.add_argument(
        "--max-message-chars",
        type=int,
        default=3500,
        help="Clip each message to this many characters before sending",
    )
    parser.add_argument(
        "--keep-recent-generation-messages",
        type=int,
        default=6,
        help="Keep only the latest generation messages (excluding the system message)",
    )
    parser.add_argument(
        "--generation-system-prompt",
        default=DEFAULT_GENERATION_SYSTEM_PROMPT,
        help="System prompt used by the generation model",
    )
    parser.add_argument(
        "--reflection-system-prompt",
        default=DEFAULT_REFLECTION_SYSTEM_PROMPT,
        help="System prompt used by the reflection model",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    agent = ReflectionAgent(
        model=args.model or DEFAULT_MODEL,
        max_completion_tokens=args.max_completion_tokens,
        max_message_chars=args.max_message_chars,
        keep_recent_generation_messages=args.keep_recent_generation_messages,
    )
    final_response = agent.run(
        user_msg=args.prompt,
        generation_system_prompt=args.generation_system_prompt,
        reflection_system_prompt=args.reflection_system_prompt,
        n_steps=args.steps,
        verbose=args.verbose,
    )
    print(final_response)


if __name__ == "__main__":
    main()
