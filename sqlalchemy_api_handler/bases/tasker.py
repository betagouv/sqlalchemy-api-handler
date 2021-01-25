import sys
from datetime import datetime
from traceback import format_exception
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func


from sqlalchemy_api_handler.bases.activator import Activator
from sqlalchemy_api_handler.mixins.task_mixin import TaskState
from sqlalchemy_api_handler.utils.date import strptime


class Tasker(Activator):

    @classmethod
    def set_celery(cls, celery_app, flask_app):
        module = sys.modules['celery.signals']
        Task = Activator.model_from_name('Task')
        BaseTask = celery_app.Task
        db = Activator.get_db()
        task_db_session = sys.modules['flask_sqlalchemy'].SQLAlchemy().session

        class AppTask(BaseTask):
            abstract = True
            '''
            *_publish tasks run into APP
            task_* and after_return run into WORKER
            '''

            # see https://github.com/kwiersma/flask-celery-sqlalchemy/blob/master/app/celeryapp/__init__.py#L89
            def __call__(self, *args, **kwargs):
                if not celery_app.conf.CELERY_ALWAYS_EAGER:
                    with flask_app.app_context():
                        return BaseTask.__call__(self, *args, **kwargs)
                return BaseTask.__call__(self, *args, **kwargs)

            @module.before_task_publish.connect
            def create_task(body, headers, routing_key, **kwargs):
                celeryUuid = headers['id']
                task_entity = Task.query.filter_by(celeryUuid=celeryUuid).first()
                if task_entity:
                    task_entity.state = TaskState.RERUNNED
                else:
                    task_entity = Task(args=body[0],
                                       celeryUuid=headers['id'],
                                       creationTime=datetime.utcnow(),
                                       isEager=False,
                                       kwargs=body[1],
                                       name=headers['task'],
                                       planificationTime=strptime('{}Z'.format(headers['eta']).replace('+00:00', '')) \
                                                  if headers.get('eta') else None,
                                       queue=routing_key,
                                       state=TaskState.CREATED)
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.after_task_publish.connect
            def modify_task_to_published_state(headers, **kwargs):
                task_entity = task_db_session.query(Task) \
                                             .filter_by(celeryUuid=headers['id']) \
                                             .one()
                task_entity.state = TaskState.PUBLISHED
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.task_received.connect
            def modify_task_to_received_state(request, sender, **kwargs):
                task_entity = task_db_session.query(Task) \
                                             .filter_by(celeryUuid=request.id) \
                                             .first()
                if not task_entity:
                    task_entity = Task(celeryUuid=request.id,
                                       name=request.task.name)
                task_entity.hostname = sender.hostname
                task_entity.state = TaskState.RECEIVED
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.task_prerun.connect
            def modify_task_to_started_state(task_id, task, **kwargs):
                if task.request.is_eager:
                    task_entity = Task(celeryUuid=task_id,
                                       isEager=True,
                                       name=task.name)
                else:
                    task_entity = task_db_session.query(Task) \
                                                 .filter_by(celeryUuid=task_id) \
                                                 .one()
                task_entity.startTime = datetime.utcnow()
                task_entity.state = TaskState.STARTED
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.task_failure.connect
            def modify_task_to_failure_state(sender, traceback, **kwargs):
                task_entity = task_db_session.query(Task) \
                                             .filter_by(celeryUuid=sender.request.id) \
                                             .one()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                task_entity.traceback = ' '.join(format_exception(exc_type,
                                                                  exc_value,
                                                                  traceback))
                task_entity.stopTime = datetime.utcnow()
                task_entity.state = TaskState.FAILED
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.task_success.connect
            def modify_task_to_success_state(sender, result, **kwargs):
                task_entity = task_db_session.query(Task) \
                                             .filter_by(celeryUuid=sender.request.id) \
                                             .one()
                task_entity.result = result
                task_entity.stopTime = datetime.utcnow()
                task_entity.state = TaskState.SUCCEED
                task_db_session.add(task_entity)
                task_db_session.commit()

            @module.task_postrun.connect
            def remove_session(*args, **kwargs):
                task_db_session.remove()

            @module.task_revoked.connect
            def modify_task_to_revoked_state(request, **kwargs):
                task_entity = task_db_session.query(Task) \
                                             .filter_by(celeryUuid=request.id) \
                                             .one()
                task_entity.stopTime = datetime.utcnow()
                task.state = TaskState.STOPPED
                task_db_session.add(task_entity)
                task_db_session.commit()
                task_db_session.remove()

            # see https://github.com/kwiersma/flask-celery-sqlalchemy/blob/master/app/celeryapp/__init__.py#L89
            def after_return(self, status, retval, task_id, args, kwargs, einfo):
                if not celery_app.conf.CELERY_ALWAYS_EAGER:
                    db.session.remove()

        celery_app.Task = AppTask

    def downgrade(op):
        op.drop_table('task')
        task_state = sa.Enum(name='taskstate')
        task_state.drop(op.get_bind())

    def upgrade(op):
        task_state = sa.Enum('CREATED',
                             'FAILED',
                             'PUBLISHED',
                             'RECEIVED',
                             'RERUNNED',
                             'STARTED',
                             'STOPPED',
                             'SUCCEED',
                              name='taskstate')
        op.create_table('task',
                        sa.Column('args', JSON()),
                        sa.Column('celeryUuid',
                                  UUID(as_uuid=True),
                                  index=True,
                                  nullable=False),
                        sa.Column('creationTime',
                                  sa.DateTime(),
                                  nullable=False,
                                  server_default=func.now()),
                        sa.Column('hostname',
                                  sa.String(64)),
                        sa.Column('isEager',
                                  sa.Boolean()),
                        sa.Column('kwargs',
                                  JSON()),
                        sa.Column('name',
                                  sa.String(256),
                                  nullable=False),
                        sa.Column('queue',
                                  sa.String(64)),
                        sa.Column('planificationTime',
                                  sa.DateTime()),
                        sa.Column('result',
                                  JSON()),
                        sa.Column('state',
                                  sa.Enum(TaskState),
                                  nullable=False),
                        sa.Column('startTime',
                                  sa.DateTime()),
                        sa.Column('stopTime',
                                  sa.DateTime()),
                        sa.Column('traceback',
                                  sa.Text()))
