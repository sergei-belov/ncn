import asyncio
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from functools import partial
from time import monotonic
from typing import (
    Callable,
    Optional,
)

import loguru

from libs.cp_common.services.base import BaseService


class ProcessManager(BaseService):
    """
    A class to manage process execution using ProcessPoolExecutor with periodic restarts.

    Attributes:
        restart (bool): Flag to indicate if the executor needs to be restarted.
        executor (generator): Generator for ProcessPoolExecutor instances.
        logger (loguru.logger): Logger instance for logging messages.

    Methods:
        execute(function, *args, **kwargs): Executes the given function with the specified arguments in a separate process.
    """

    def __init__(
        self,
        restart_time: int = 600,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        max_workers: Optional[int] = None,
        max_executions: Optional[int] = None,
        initializer: Optional[Callable] = None,
    ):
        """Initialize process-pool lifecycle and restart settings.

        Args:
            restart_time: Seconds between scheduled executor restarts.
            loop: Event loop used to submit process work.
            max_workers: Maximum worker processes in each executor.
            max_executions: Optional executions allowed before recycling a pool.
            initializer: Optional callable invoked in each worker process.
        """
        super().__init__()
        self.restart = None
        self.process = None
        self.executor = None
        self.max_workers = max_workers
        self._loop = loop
        self.logger = loguru.logger
        self.restart_time = restart_time
        self.initializer = initializer

        self.max_executions = max_executions
        self.counter = 0

    async def execute(self, function: Callable, timeout: float | None = None, **kwargs) -> (float, tuple):
        """
        Executes the given function with the specified arguments in a separate process.

        Args:
            function (Callable): The function to be executed.
            timeout (None | float): function execution timeout
            **kwargs: Arbitrary keyword arguments for the function.

        Returns:
            The result of the function execution.
        """
        executor = next(self.executor)
        cpu_bound = partial(function, **kwargs)

        try:
            start_time = monotonic()
            future = self._loop.run_in_executor(executor, cpu_bound)
            result = await asyncio.wait_for(future, timeout)
            exec_time = monotonic() - start_time
            return exec_time, result
        except BrokenProcessPool:
            self.restart = True
            raise BrokenProcessPool
        except Exception as e:
            raise e

    async def _reloader(self, restart_time: int = 600):
        """Mark the active executor for periodic recycling.

        Args:
            restart_time: Seconds between restart requests.
        """
        while self.process:
            await asyncio.sleep(restart_time)
            self.restart = True

    def _executor(self):
        """Yield process-pool executors until the manager stops."""

        while self.process:
            self.restart = False
            self.counter = 0

            with ProcessPoolExecutor(max_workers=self.max_workers, initializer=self.initializer) as executor:

                while not self.restart and self.process:
                    yield executor
                    if self.max_executions:
                        self.counter += 1
                        if self.counter >= self.max_executions:
                            break

            self.logger.info("Process executor reloaded")
        self.logger.info("Process executor stopped")

    async def start(self):
        """Start executor generation and the periodic reloader task."""

        self.process = True
        self._loop = self._loop or asyncio.get_event_loop()
        self._loop.create_task(self._reloader(self.restart_time))
        self.executor = self._executor()

    async def stop(self):
        """Stop executor generation and close the current process pool."""

        self.process = False

        try:
            next(self.executor)
        except StopIteration:
            pass

    async def ping(self) -> bool:
        """Return the process manager's static health status."""

        return True
