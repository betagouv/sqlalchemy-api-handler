from time import sleep
from itertools import chain
from functools import partial
from concurrent.futures import ThreadPoolExecutor


def chunks_from(elements, chunk_by=None):
    length = chunk_by if chunk_by else len(elements)
    for index in range(0, len(elements), length):
        yield elements[index:index + length]


def zipped_async_map(func,
                     args_list=None,
                     kwargs_list=None,
                     chunk_by=None,
                     executor_class=None,
                     max_workers=5,
                     sleep_between=None):

    if args_list and kwargs_list:
        listed_args_list = list(args_list)
        listed_kwargs_list = list(kwargs_list)
        if len(listed_args_list) != len(listed_kwargs_list):
            raise 'args_list and kwargs_list must have the same length.'
        args_chunks = list(chunks_from(listed_args_list, chunk_by))
        kwargs_chunks = list(chunks_from(listed_kwargs_list, chunk_by))
        chunks_count = len(args_chunks)
    elif args_list and not kwargs_list:
        listed_args_list = list(args_list)
        if len(listed_args_list) == 0:
            return []
        args_chunks = list(chunks_from(listed_args_list, chunk_by))
        kwargs_chunks = None
        chunks_count = len(args_chunks)
    elif kwargs_list:
        listed_kwargs_list = list(kwargs_list)
        if len(listed_kwargs_list) == 0:
            return []
        args_chunks = None
        kwargs_chunks = list(chunks_from(listed_kwargs_list, chunk_by))
        chunks_count = len(kwargs_chunks)
    elif args_list is None and kwargs_list is None:
        raise 'one args_list or kwargs_list need to be specified.'
    else:
        return []

    if executor_class is None:
        executor_class = ThreadPoolExecutor

    def asynchronous_func(args_and_kwargs):
        return func(*args_and_kwargs[0], **args_and_kwargs[1])


    results = []
    with executor_class(max_workers=max_workers) as executor:
        for index in range(0, chunks_count):
            args_list = args_chunks[index] if args_chunks else None
            kwargs_list = kwargs_chunks[index] if kwargs_chunks else None
            if args_list and kwargs_list:
                if len(args_list) != len(kwargs_list):
                    raise 'args_list and kwargs_list must have the same length.'
            elif args_list and not kwargs_list:
                kwargs_list = [{}]*len(args_list)
            elif kwargs_list:
                args_list = [()]*len(kwargs_list)
            results = chain(results,
                            executor.map(asynchronous_func,
                                         zip(args_list, kwargs_list)))
            if sleep_between:
                sleep(sleep_between)
        return results


def async_map(func, *lists, **kwargs):
    return zipped_async_map(func, zip(*lists), **kwargs)
