# Repository Guidelines

## Project Structure & Module Organization
- Core Python implementations live in `src/`, split by pattern: `tool_pattern/`, `reflection_pattern/`, `planning_pattern/`, and `multiagent_pattern/`.
- Interactive exploration lives in `notebooks/` (`*_pattern.ipynb`), which are code-first and output-cleared.
- Dependencies are tracked in `requirements.txt`; local secrets belong in `.env` (do not commit).
- Note: `planning_pattern` and `multiagent_pattern` currently rely on the external `agentic_patterns` package, while `tool_pattern` and `reflection_pattern` are implemented locally.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate`: create and activate local environment.
- `pip install -r requirements.txt`: install baseline dependencies.
- `pip install colorama graphviz`: install extras required by planning/multi-agent flows.
- `jupyter notebook`: run notebooks in `notebooks/`.
- `python -m src.reflection_pattern "<prompt>" --steps 3 --verbose 1`: run the reflection agent from CLI.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and clear type hints (`list[dict[str, str]]`, `Optional[...]`).
- Prefer small dataclass-based agents and explicit constants for defaults (for example `DEFAULT_MODEL`).
- Use snake_case for modules, files, variables, and functions; use PascalCase for classes (`ToolAgent`, `ReflectionAgent`).
- Keep functions focused and side effects explicit (API calls, env loading, logging).

## Testing Guidelines
- There is no dedicated `tests/` suite yet; validate changes with targeted runs:
  - module smoke test via `python -m src.reflection_pattern ...`
  - notebook execution for affected pattern(s)
- When adding tests, use `tests/` with `test_*.py` naming and prioritize agent loop behavior, tool-call parsing, and error handling.

## Commit & Pull Request Guidelines
- Follow existing Conventional Commit style seen in history: `feat: ...`, `fix: ...`.
- Keep commits scoped to one pattern or concern.
- PRs should include:
  - concise summary of behavior change
  - linked issue/context (if available)
  - reproduction/verification commands run locally
  - screenshots only when notebook output or visuals materially changed

## Security & Configuration Tips
- Required keys are loaded from `.env` (for example `GROQ_API_KEY`, optional `WEATHER_API_KEY`).
- Never hardcode keys or commit `.env`; use environment variables in all examples and scripts.
