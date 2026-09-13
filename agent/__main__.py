"""Run the pricing agent: python -m agent "quote 5000 flat cards"."""

from __future__ import annotations

import sys

from .graph import build_agent


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or "What is the current quote?"
    agent = build_agent()
    result = agent.invoke({"messages": [("user", prompt)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
