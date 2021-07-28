from asyncio import TimeoutError, sleep, wait_for
from pathlib import Path
from typing import Callable


class Waiter:
    def __init__(self, fucntion: Callable[[], bool],
                 timeout: float = 1.) -> None:
        self.fucntion = fucntion
        self.timeout = timeout

    async def wait_without_timeout(self) -> bool:
        while not self.fucntion():
            await sleep(self.timeout)

        return True

    async def wait(self) -> bool:
        try:
            await wait_for(self.wait_without_timeout(),
                           timeout=self.timeout)
            return True
        except TimeoutError:
            return False


class PathWaiter(Waiter):
    def __init__(self, path: Path = Path().cwd(),
                 timeout: float = 1.) -> None:
        self.path = path
        super().__init__(self.does_the_path_exist,
                         timeout=timeout)

    def does_the_path_exist(self) -> bool:
        return self.path.exists()

