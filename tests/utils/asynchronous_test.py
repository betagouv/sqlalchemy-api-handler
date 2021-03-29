import pytest
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy_api_handler.utils.asynchronous import async_map, zipped_async_map


class AsynchronousTest:
    def test_zipped_async_map_with_args_list(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(zipped_async_map(add,
                                        [(first_call_a, first_call_b), (second_call_a, second_call_b)]))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b

    def test_zipped_async_map_with_args_list_and_kwargs_list(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def op(a, b, action='add'):
            if action == 'add':
                return a + b
            elif action == 'substract':
                return a - b
            return None

        # When
        results = list(zipped_async_map(op,
                                        [(first_call_a, first_call_b), (second_call_a, second_call_b)],
                                        [{ 'action': 'add' }, { 'action': 'substract'}]))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a - second_call_b

    def test_zipped_async_map_with_kwargs_list(self, app):
        # Given
        def op(action='add'):
            if action == 'add':
                return 1 + 1
            elif action == 'substract':
                return 1 - 1
            return None

        # When
        results = list(zipped_async_map(op,
                                        None,
                                        [{ 'action': 'add' }, { 'action': 'substract'}]))

        # Then
        assert results[0] == 2
        assert results[1] == 0

    def test_add_function_with_simple_map(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(map(add,
                           (first_call_a, second_call_a),
                           (first_call_b, second_call_b)))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b


    def test_add_function_with_async_map(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(async_map(add,
                                 (first_call_a, second_call_a),
                                 (first_call_b, second_call_b)))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b

    def test_add_function_with_custom_async_map(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(async_map(add,
                                 (first_call_a, second_call_a),
                                 (first_call_b, second_call_b),
                                 executor_class=ThreadPoolExecutor,
                                 max_workers=2))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b


    def test_add_function_with_chunks(self, app):
        # Given
        def add(*args):
            result = 0
            for arg in args:
                result += arg
            return result

        # When
        results = list(async_map(add,
                                 list(range(0, 10)),
                                 [index + 1 for index in range(0, 10)],
                                 chunk_by=5))

        # Then
        assert results == [2*index + 1 for index in range(0, 10)]
