import asyncio
from asyncio import Future
from typing import Awaitable, TypeVar, Union

_T = TypeVar("_T")
_FutureT = Union[Future[_T], Awaitable[_T]]


async def gather_with_safe_exceptions(*tasks: _FutureT[_T]) -> list[_T]:
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            raise result
    return results


async def gather_with_concurrency(limit: int, *tasks: _FutureT[_T]) -> list[_T]:
    semaphore = asyncio.Semaphore(limit)

    async def sem_task(task: _FutureT[_T]) -> _T:
        async with semaphore:
            return await task

    return await gather_with_safe_exceptions(*(sem_task(task) for task in tasks))
