from typing import Optional, Dict, Any

from pydantic import Field

from openmanus.tool.base import BaseTool
from openmanus.logger import logger

class EnhancedAgentTool(BaseTool):
    """
    Tool that delegates to the enhanced agent for complex tasks requiring research
    or multi-step reasoning. This tool acts as a bridge between the main OpenManus
    agent and the enhanced research agent.
    """

    name: str = "enhanced_agent"
    description: str = (
        "Useful for complex tasks that require research, multi-step reasoning, "
        "or when the main agent needs assistance. Input should be a detailed "
        "description of what you need, including any specific requirements or context."
    )
    enabled: bool = True

    # Instance variables (not Pydantic fields)
    _agent: Optional[Any] = None
    _run_enhanced_agent: Optional[Any] = None

    def __init__(self, **data):
        """Initialize the tool and create the enhanced agent instance."""
        super().__init__(**data)
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the enhanced agent instance."""
        try:
            from enhanced_agent.src.app import create_agent, run_enhanced_agent
            self._agent = create_agent()
            self._run_enhanced_agent = run_enhanced_agent
            logger.info("Enhanced agent instance created successfully")
        except ImportError as e:
            logger.warning(f"Failed to import enhanced_agent: {e}")
            self._agent = None
            self._run_enhanced_agent = None
        except Exception as e:
            logger.warning(f"Failed to initialize enhanced agent: {e}")
            self._agent = None
            self._run_enhanced_agent = None

    async def _run(self, input_text: str) -> str:
        """
        Execute the enhanced agent with the given input.

        Args:
            input_text: The task or question for the enhanced agent

        Returns:
            str: The enhanced agent's response
        """
        try:
            if self._agent is None or self._run_enhanced_agent is None:
                return (
                    "Enhanced agent is not available. Please ensure the enhanced_agent "
                    "package is properly installed and configured."
                )

            logger.info(f"Delegating to enhanced agent with input: {input_text[:200]}...")
            result = await self._run_enhanced_agent(input_text, agent=self._agent)
            logger.info("Enhanced agent completed successfully")
            return result
            
        except ImportError as e:
            error_msg = (
                "Failed to import enhanced_agent. Please ensure it's installed. "
                f"Error: {str(e)}"
            )
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"Error in enhanced agent execution: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _arun(self, input_text: str) -> str:
        """Async implementation of the tool."""
        return await self._run(input_text)
