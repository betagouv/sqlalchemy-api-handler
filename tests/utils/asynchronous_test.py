import pytest

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
        results = list(zipped_async_map(add, [(first_call_a, first_call_b), (second_call_a, second_call_b)]))

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


    def test_map(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(map(add, (first_call_a, second_call_a), (first_call_b, second_call_b)))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b


    def test_async_map(self, app):
        # Given
        first_call_a = 1
        first_call_b = 2
        second_call_a = 3
        second_call_b = 4
        def add(a, b):
            return a + b

        # When
        results = list(async_map(add, (first_call_a, second_call_a), (first_call_b, second_call_b)))

        # Then
        assert results[0] == first_call_a + first_call_b
        assert results[1] == second_call_a + second_call_b
