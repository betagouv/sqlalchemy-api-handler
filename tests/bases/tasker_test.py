# pylint: disable=R0201
# pylint: disable=W0613

import pytest
from sqlalchemy_api_handler.mixins import TaskState

from tests.conftest import with_delete
from api.models.task import Task
from api.tasks.hello import print_text


class TaskerTest:
    @with_delete
    def test_create_eager_task(self, app):
        # Given
        text = 'Karl !'

        # When
        print_text.apply(args=(text,)).get()

        # Then
        task = Task.query.first()
        assert task.isEager == True
        assert task.name == 'api.tasks.hello.print_text'
        assert task.state == TaskState.SUCCEED
        assert task.result == { 'text': text }
