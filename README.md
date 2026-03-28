# Agent Patterns

`agent-patterns` is a small learning repo for experimenting with common LLM agent design patterns:

- `tool_pattern`: let a model decide when to call tools
- `reflection_pattern`: alternate between generation and critique
- `planning_pattern`: run a ReAct-style loop with tools
- `multiagent_pattern`: compose multiple agents with dependencies

The repo mixes two kinds of artifacts:

- runnable Python modules in [`src/`](/Users/ayushamin/Developer/repos/agent-patterns/src)
- Jupyter notebooks in [`notebooks/`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks) for interactive exploration

## Repo Layout

```text
.
├── notebooks/
│   ├── tool_pattern.ipynb
│   ├── reflection_pattern.ipynb
│   ├── planning_pattern.ipynb
│   └── multiagent_pattern.ipynb
├── src/
│   ├── tool_pattern/
│   ├── reflection_pattern/
│   ├── planning_pattern/
│   └── multiagent_pattern/
└── requirements.txt
```

## Current State

There is some implementation drift in the repo right now, so it helps to know what is local vs external:

- [`src/tool_pattern`](/Users/ayushamin/Developer/repos/agent-patterns/src/tool_pattern) contains a local `Tool` abstraction and `ToolAgent`.
- [`src/reflection_pattern`](/Users/ayushamin/Developer/repos/agent-patterns/src/reflection_pattern) contains a local `ReflectionAgent` and a small CLI entrypoint.
- [`src/planning_pattern/agent.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/planning_pattern/agent.py) and the multi-agent code still import from the external `agentic_patterns` package.
- The notebooks have been trimmed to code-only cells for easier execution, so the narrative/tutorial markdown is no longer present inside them.

## Requirements

The current dependency list is in [requirements.txt](/Users/ayushamin/Developer/repos/agent-patterns/requirements.txt):

```txt
groq
python-dotenv
ipython
jupyter
requests
agentic_patterns
```

Some source files also expect packages that are not currently pinned here, especially for the planning and multi-agent flows:

- `colorama`
- `graphviz`

If you want every pattern to run smoothly, install those too.

## Setup

### 1. Create an environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install colorama graphviz
```

### 2. Configure environment variables

Create a `.env` file in the repo root.

For the local source modules currently in `src/`, the default provider is Groq, so you will usually need:

```env
GROQ_API_KEY=your_key_here
```

For the weather example in the tool notebook:

```env
WEATHER_API_KEY=your_weatherapi_key_here
```

### 3. Start Jupyter

```bash
jupyter notebook
```

Open the notebook you want from [`notebooks/`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks).

## Pattern Overview

### Tool Pattern

Files:

- [`src/tool_pattern/tool.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/tool_pattern/tool.py)
- [`src/tool_pattern/agent.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/tool_pattern/agent.py)
- [`notebooks/tool_pattern.ipynb`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks/tool_pattern.ipynb)

What it demonstrates:

- converting Python callables into tool descriptors
- exposing tool signatures to the model
- letting the model decide whether to answer directly or emit a tool call
- executing the tool and feeding the result back into the model

Core local API:

```python
from src.tool_pattern import ToolAgent, tool

@tool
def fetch_status(service: str) -> str:
    """Fetch service status."""
    return f"{service} is healthy"

agent = ToolAgent(tools=[fetch_status])
print(agent.run("Check the status of payments"))
```

Notes:

- The local `tool()` helper builds a JSON-like function signature from a Python function signature and docstring.
- `ToolAgent` expects the model to return either `<tool_call>...</tool_call>` or `<final_answer>...</final_answer>`.

### Reflection Pattern

Files:

- [`src/reflection_pattern/agent.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/reflection_pattern/agent.py)
- [`src/reflection_pattern/__main__.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/reflection_pattern/__main__.py)
- [`notebooks/reflection_pattern.ipynb`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks/reflection_pattern.ipynb)

What it demonstrates:

- generating an initial answer
- critiquing that answer
- feeding the critique back into the generator
- repeating for a fixed number of steps

Python usage:

```python
from src.reflection_pattern import ReflectionAgent

agent = ReflectionAgent()
result = agent.run(
    user_msg="Write a clean Python implementation of merge sort.",
    n_steps=3,
    verbose=1,
)
print(result)
```

CLI usage:

```bash
python -m src.reflection_pattern "Write a bubble sort in Python" --steps 3 --verbose 1
```

Helpful knobs:

- `--steps`
- `--model`
- `--max-completion-tokens`
- `--max-message-chars`
- `--keep-recent-generation-messages`

### Planning Pattern

Files:

- [`src/planning_pattern/agent.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/planning_pattern/agent.py)
- [`notebooks/planning_pattern.ipynb`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks/planning_pattern.ipynb)

What it demonstrates:

- a ReAct loop
- explicit `Thought -> Action -> Observation` structure
- repeated tool usage until a final response is produced

Important caveat:

- This code currently depends on the external `agentic_patterns` package for `Tool`, `ChatHistory`, completion helpers, extraction helpers, and argument validation.
- It is not yet aligned with the local `src/tool_pattern` implementation.

### Multi-Agent Pattern

Files:

- [`src/multiagent_pattern/agent.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/multiagent_pattern/agent.py)
- [`src/multiagent_pattern/crew.py`](/Users/ayushamin/Developer/repos/agent-patterns/src/multiagent_pattern/crew.py)
- [`notebooks/multiagent_pattern.ipynb`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks/multiagent_pattern.ipynb)

What it demonstrates:

- defining multiple agents with distinct tasks
- wiring dependencies between agents with `>>` / `<<`
- passing context from one agent to another
- executing a dependency graph in topological order with `Crew`

Sketch:

```python
from agentic_patterns.multiagent_pattern.agent import Agent
from agentic_patterns.multiagent_pattern.crew import Crew

with Crew() as crew:
    researcher = Agent(
        name="Researcher",
        backstory="You gather useful facts.",
        task_description="Find the most relevant facts about the topic.",
    )
    writer = Agent(
        name="Writer",
        backstory="You write concise summaries.",
        task_description="Write a summary using the provided context.",
    )

    researcher >> writer
    crew.run()
```

Important caveat:

- Like the planning pattern, this code still relies on the external `agentic_patterns` package.

## Notebooks

The notebooks in [`notebooks/`](/Users/ayushamin/Developer/repos/agent-patterns/notebooks) are currently code-only versions. That means:

- markdown explanation cells were removed
- image cells were removed
- saved outputs were cleared

This makes them easier to rerun, but you should not expect tutorial prose inside the notebooks themselves.

## Troubleshooting

### `ModuleNotFoundError: No module named 'groq'`

Install dependencies into the same Python environment that Jupyter or your script is using:

```bash
pip install -r requirements.txt
```

### `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

That usually means your installed `groq` and `httpx` versions are incompatible. A common fix is:

```bash
pip install "httpx<0.28"
```

### Notebook imports fail

If you run notebooks from inside `notebooks/`, local imports may behave differently than when running from the repo root. The safest path is:

- launch Jupyter from the repository root
- keep the repo root on `sys.path` when needed

### Planning or multi-agent examples fail even though `tool_pattern` works

That is likely because the planning and multi-agent implementations still depend on the external `agentic_patterns` package, not just the local `src/` modules.

## Suggested Next Steps

If you want to keep building this repo out, the highest-leverage cleanup tasks are:

1. Unify all patterns under the local `src/` package instead of mixing local and external implementations.
2. Add a proper packaging file (`pyproject.toml`) so installation is reproducible.
3. Pin fully compatible dependency versions in [requirements.txt](/Users/ayushamin/Developer/repos/agent-patterns/requirements.txt).
4. Add a minimal test suite for the core agents.
5. Decide on one model provider path for the whole repo instead of mixing experiments over time.

## License

No license file is currently present in the repository. If you plan to share or publish this project, adding one would be a good next step.
