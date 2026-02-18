import asyncio
from typing import Any

# Default concurrency limit for fan-out backend calls
DEFAULT_CONCURRENCY_LIMIT = 10


async def limited_gather(*coroutines, max_concurrent: int = DEFAULT_CONCURRENCY_LIMIT, return_exceptions: bool = False) -> list[Any]:
    """
    A drop-in replacement for asyncio.gather that limits the number of 
    concurrently running coroutines using a semaphore.
    
    This prevents overwhelming the backend when fan-out patterns (e.g., 
    processing 30 portfolios in parallel) generate excessive concurrent requests.
    
    Args:
        *coroutines: Coroutines to execute.
        max_concurrent: Maximum number of coroutines to run simultaneously. Default is 5.
        return_exceptions: If True, exceptions are returned as results instead of being raised.
    
    Returns:
        List of results from the coroutines, in the same order as the input.
    
    Usage:
        # Before (unlimited fan-out):
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # After (limited to 5 concurrent):
        results = await limited_gather(*tasks, return_exceptions=True)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _limited(coro):
        async with semaphore:
            return await coro
    
    return await asyncio.gather(
        *[_limited(coro) for coro in coroutines],
        return_exceptions=return_exceptions
    )
