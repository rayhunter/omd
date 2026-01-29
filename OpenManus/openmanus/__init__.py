"""
OpenManus: General-purpose AI agent framework with browser automation and tool integration.
"""

# Python version check: 3.10-3.13
import sys


if sys.version_info < (3, 10) or sys.version_info > (3, 13):
    print(
        "Warning: Unsupported Python version {ver}, please use 3.10-3.13".format(
            ver=".".join(map(str, sys.version_info))
        )
    )

__version__ = "0.1.0"

# Import main components for easier access
from openmanus.agent.manus import Manus
from openmanus.agent.base import BaseAgent
from openmanus.agent.react import ReActAgent
from openmanus.agent.toolcall import ToolCallAgent

__all__ = ["Manus", "BaseAgent", "ReActAgent", "ToolCallAgent", "__version__"]
