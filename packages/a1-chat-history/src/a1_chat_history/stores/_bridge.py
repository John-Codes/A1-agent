"""Runs motor coroutines on a dedicated event loop so sync store code can block on results."""
import asyncio
import threading


class AsyncBridge:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()

    async def _resolve(self, awaitable):
        return await awaitable

    def call(self, awaitable, timeout=30):
        future = asyncio.run_coroutine_threadsafe(self._resolve(awaitable), self._loop)
        return future.result(timeout)
