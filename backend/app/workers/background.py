import asyncio
from typing import Callable


class BackgroundWorker:
    """A lightweight async worker abstraction for CPU-light background tasks.

    This intentionally avoids adding a heavy Celery/RQ dependency for a portfolio project,
    but keeps the architecture ready to scale to distributed workers later.
    """

    def __init__(self):
        self._tasks: set[asyncio.Task] = set()

    def enqueue(self, coro_factory: Callable[[], asyncio.Future], *, name: str | None = None):
        async def runner():
            await coro_factory()

        task = asyncio.create_task(runner(), name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
