import abc
import asyncio
import logging
from typing import Any, List, Union

import tqdm

logger = logging.getLogger(__name__)


class AsyncTask(abc.ABC):
    @abc.abstractmethod
    async def _do_task(self, data: Any):
        pass

    async def _do_task_with_index(self, idx: int, data: Any, sem: asyncio.Semaphore):
        async with sem:
            return idx, await self._do_task(data)

    async def async_apply(
        self,
        data_list: List[Any],
        tqdm_desc: Union[str, None] = None,
        concurrency: int = 100,
    ):

        sem = asyncio.Semaphore(concurrency)
        tasks = [self._do_task_with_index(idx, data, sem) for idx, data in enumerate(data_list)]
        responses = [
            await f
            for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=tqdm_desc)
        ]

        # Re-order responses
        responses = [response[1] for response in sorted(responses, key=lambda x: x[0])]

        return responses

    def apply(
        self,
        data_list: List[Any],
        tqdm_desc: Union[str, None] = None,
        concurrency: int = 100,
    ):

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.async_apply(data_list=data_list, tqdm_desc=tqdm_desc, concurrency=concurrency)
        )


if __name__ == "__main__":
    import random

    class TestAsyncTask(AsyncTask):
        async def _do_task(self, data: Any):
            print(f"wait {data} seconds...")
            await asyncio.sleep(data)
            return f"waited {data} seconds"

    t = TestAsyncTask()
    r = t.apply(data_list=[random.randrange(2) for i in range(100)], concurrency=10)
