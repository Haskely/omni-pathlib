import asyncio
import sys

if sys.platform == "win32":
    from asyncio import WindowsSelectorEventLoopPolicy

    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
else:
    asyncio.set_event_loop_policy(
        asyncio.DefaultEventLoopPolicy()
    )  # Fallback for other platforms
