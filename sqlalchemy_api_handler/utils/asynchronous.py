# https://medium.com/hackernoon/how-to-run-asynchronous-web-requests-in-parallel-with-python-3-5-without-aiohttp-264dc0f8546
from time import sleep
from functools import partial
import asyncio
from concurrent.futures import ThreadPoolExecutor


def chunks_from(elements, chunk_by=None):
    length = chunk_by if chunk_by else len(elements)
    for index in range(0, len(elements), length):
        yield elements[index:index + length]


def create_asynchronous(func,
                        args_list=None,
                        kwargs_list=None,
                        max_workers=10):
    if args_list and kwargs_list:
        if len(args_list) != len(kwargs_list):
            raise 'args_list and kwargs_list must have the same length.'
    elif args_list and not kwargs_list:
        kwargs_list = [{}]*len(args_list)
    elif kwargs_list:
        args_list = [()]*len(kwargs_list)

    async def asynchronous_func():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, partial(func, **kwargs), *args)
                for (args, kwargs) in zip(args_list, kwargs_list)
            ]
            return await asyncio.gather(*tasks)
    return asynchronous_func


def async_map(func,
              args_list=None,
              kwargs_list=None,
              chunk_by=None,
              max_workers=None,
              sleep_between=None):
    if args_list and kwargs_list:
        listed_args_list = list(args_list)
        listed_kwargs_list = list(kwargs_list)
        if len(listed_args_list) != len(listed_kwargs_list):
            raise 'args_list and kwargs_list must have the same length.'
        args_chunks = list(chunks_from(listed_args_list, chunk_by))
        kwargs_chunks = list(chunks_from(listed_kwargs_list, chunk_by))
    elif args_list and not kwargs_list:
        listed_args_list = list(args_list)
        if len(listed_args_list) == 0:
            return []
        args_chunks = list(chunks_from(listed_args_list, chunk_by))
        kwargs_chunks = None
    elif kwargs_list:
        listed_kwargs_list = list(kwargs_list)
        if len(listed_kwargs_list) == 0:
            return []
        args_chunks = None
        kwargs_chunks = list(chunks_from(listed_kwargs_list, chunk_by))
    elif args_list is None and kwargs_list is None:
        raise 'one args_list or kwargs_list need to be specified.'
    else:
        return []

    results = []
    for index in range(0, len(args_chunks)):
        asynchronous_func = create_asynchronous(func,
                                                args_list=args_chunks[index] if args_chunks else None,
                                                kwargs_list=kwargs_chunks[index] if kwargs_chunks else None,
                                                max_workers=max_workers)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(asynchronous_func())
        loop.run_until_complete(future)
        results += future.result()
        if sleep_between:
            sleep(sleep_between)
    return results
