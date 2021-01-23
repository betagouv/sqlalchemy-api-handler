from functools import reduce
from itertools import groupby
from sqlalchemy import BigInteger, desc
from postgresql_audit.flask import versioning_manager

from sqlalchemy_api_handler.bases.accessor import Accessor
from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.bases.save import Save
from sqlalchemy_api_handler.utils.datum import relationships_in
from sqlalchemy_api_handler.utils.logger import logger


def merged_datum_from_activities(activities,
                                 model,
                                 initial=None):
    return reduce(lambda agg, activity: {**agg, **relationships_in(activity.patch, model)},
                  activities,
                  relationships_in(initial, model) if initial else {})


class Activator(Save):

    @classmethod
    def get_activity(cls):
        return Activator.activity_cls

    @classmethod
    def set_activity(cls, activity_cls):
        Activator.activity_cls = activity_cls

    @staticmethod
    def activate(*activities,
                 with_check_not_soft_deleted=True):
        Activity = Activator.get_activity()
        for (entity_identifier, grouped_activities) in groupby(activities, key=lambda activity: activity.entityIdentifier):
            grouped_activities = sorted(grouped_activities, key=lambda activity: activity.dateCreated)

            first_activity = grouped_activities[0]
            table_name = first_activity.table_name
            model = Save.model_from_table_name(table_name)
            id_key = model.id.property.key

            if first_activity.verb == 'delete':
                query = model.query.filter_by(activityIdentifier=entity_identifier)
                entity = query.one()
                entity_id = entity.id
                query.delete()
                Activator.get_db().session.commit()
                delete_activity = entity.__deleteActivity__
                delete_activity.dateCreated = first_activity.dateCreated
                Save.save(delete_activity)

                # want to make as if first_activity was the delete_activity one
                # for such route like operations
                # '''
                #    ApiHandler.activate(**activities)
                #    return jsonify([as_dict(activity) for activity in activities])
                # '''
                first_activity.id = delete_activity.id
                if delete_activity.transaction:
                    first_activity.transaction = Activity.transaction.mapper.class_()
                    first_activity.transaction.actor  = delete_activity.transaction.actor
                Activator.activate(*grouped_activities[1:],
                                   with_check_not_soft_deleted=with_check_not_soft_deleted)
                continue

            if model is None:
                errors = ActivityError()
                errors.add_error('tableName', 'model from {} not found'.format(table_name))
                raise errors

            entity = model.query.filter_by(activityIdentifier=entity_identifier).first()
            entity_id = entity.id if entity else None
            if not entity_id:
                entity = model(**relationships_in(first_activity.patch, model))
                entity.activityIdentifier = entity_identifier
                Activator.save(entity)
                insert_activity = entity.__insertActivity__
                insert_activity.dateCreated = first_activity.dateCreated
                Save.save(insert_activity)
                # want to make as if first_activity was the insert_activity one
                # very useful for the routes operation
                # '''
                #    ApiHandler.activate(**activities)
                #    return jsonify([as_dict(activity) for activity in activities])
                # '''
                first_activity.id = insert_activity.id
                first_activity.changed_data = {**insert_activity.changed_data}
                if insert_activity.transaction:
                    first_activity.transaction = Activity.transaction.mapper.class_()
                    first_activity.transaction.actor  = insert_activity.transaction.actor

                for activity in grouped_activities[1:]:
                    activity.old_data = { id_key: entity.id }
                Activator.activate(*grouped_activities[1:],
                                   with_check_not_soft_deleted=with_check_not_soft_deleted)
                continue

            min_date = min(map(lambda a: a.dateCreated, grouped_activities))
            already_activities_since_min_date = Activity.query \
                                                        .filter(
                                                            (entity._get_activity_join_filter()) & \
                                                            (Activity.dateCreated >= min_date)
                                                        ) \
                                                        .all()

            all_activities_since_min_date = sorted(already_activities_since_min_date + grouped_activities,
                                                   key=lambda activity: activity.dateCreated)
            datum = merged_datum_from_activities(all_activities_since_min_date,
                                                 model,
                                                 initial=all_activities_since_min_date[0].datum)
            if model.id.key in datum:
                del datum[model.id.key]
            entity = model.query.get(entity_id)
            entity.modify(datum,
                          with_check_not_soft_deleted=with_check_not_soft_deleted)

            Save.save(entity, *grouped_activities)


    @classmethod
    def models(cls):
        models = Accessor.models()
        Activity = cls.get_activity()
        if Activity:
            models += [Activity]
        return models


    def downgrade(op):
        op.drop_table('activity')
        op.drop_table('transaction')
        op.execute(
        '''
            DROP FUNCTION audit_table(regclass);
            DROP FUNCTION audit_table(regclass, text[]);
            DROP FUNCTION create_activity();
            DROP FUNCTION jsonb_subtract(jsonb, jsonb) CASCADE;
            DROP FUNCTION jsonb_change_key_name(jsonb, text, text);
        '''
        )

    def upgrade(op):
        from sqlalchemy_api_handler.mixins.activity_mixin import ActivityMixin
        db = Activator.get_db()
        versioning_manager.init(db.Model)
        versioning_manager.transaction_cls.__table__.create(op.get_bind())
        class Activity(ActivityMixin,
                       Activator,
                       versioning_manager.activity_cls):
            __table_args__ = {'extend_existing': True}

            id = versioning_manager.activity_cls.id
        Activity.__table__.create(op.get_bind())
        op.add_column('transaction',
                      sa.Column('actor_id',
                                sa.BigInteger()))
