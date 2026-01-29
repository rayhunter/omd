import asyncio

from openmanus.agent.manus import Manus
from openmanus.logger import logger


async def async_main():
    agent = Manus()
    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


def main():
    """Entry point for the openmanus CLI command."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
