from itertools import groupby
import sqlalchemy as sa
from postgresql_audit.flask import versioning_manager

from sqlalchemy_api_handler.bases.accessor import Accessor
from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.bases.save import Save
from sqlalchemy_api_handler.utils.datum import merged_datum_from_activities, \
                                               relationships_in


class Activate(Save):

    @classmethod
    def get_activity(cls):
        return Activate.activity_cls

    @classmethod
    def set_activity(cls, activity_cls):
        Activate.activity_cls = activity_cls

    @staticmethod
    def unknown_activities_from(activities):
        activity_class = Activate.get_activity()
        if not activities:
            return []
        potential_existing_activities = activity_class.query.filter(activity_class.entityIdentifier.in_([a.entityIdentifier for a in activities])) \
                                                            .filter(activity_class.dateCreated.in_([a.dateCreated for a in activities])) \
                                                            .all()
        potential_existing_activities_dict = { (str(a.dateCreated), str(a.entityIdentifier)) : a for a in potential_existing_activities }
        unknown_activities = []
        for activity in activities:
            existing_activity = potential_existing_activities_dict.get((str(activity.dateCreated), str(activity.entityIdentifier)))
            if existing_activity:
                for key, value in vars(existing_activity).items():
                    setattr(activity, key, value)
            else:
                unknown_activities.append(activity)
        return unknown_activities

    @staticmethod
    def activate_deletion(activity):
        model = Save.model_from_table_name(activity.table_name)
        query = model.query.filter_by(activityIdentifier=activity.entityIdentifier)
        entity = query.one()
        query.delete()
        delete_activity = entity.__deleteActivity__
        delete_activity.dateCreated = activity.dateCreated
        Save.add(delete_activity)
        # want to make as if first_activity was the delete_activity one
        # for such route like operations
        # '''
        #    ApiHandler.activate(**activities)
        #    return jsonify([as_dict(activity) for activity in activities])
        # '''
        activity.id = delete_activity.id
        if delete_activity.transaction:
            activity.transaction = Activate.get_activity().transaction.mapper.class_()
            activity.transaction.actor  = delete_activity.transaction.actor

    @staticmethod
    def activate_insertion(activity):
        model = Save.model_from_table_name(activity.table_name)
        entity = model(**relationships_in(activity.patch, model))
        entity.activityIdentifier = activity.entityIdentifier
        entity.dateCreated = activity.dateCreated
        Save.add(entity)
        Activate.get_db().session.flush()
        insert_activity = entity.__insertActivity__
        insert_activity.dateCreated = activity.dateCreated
        Save.add(insert_activity)
        # want to make as if first_activity was the insert_activity one
        # very useful for the routes operation
        # '''
        #    ApiHandler.activate(**activities)
        #    return jsonify([as_dict(activity) for activity in activities])
        # '''
        activity.id = insert_activity.id
        activity.changed_data = {**insert_activity.changed_data}
        if insert_activity.transaction:
            activity.transaction = Activate.get_activity().transaction.mapper.class_()
            activity.transaction.actor  = insert_activity.transaction.actor

    @staticmethod
    def activate_updates(activities,
                         entity,
                         with_check_not_soft_deleted=True):
        min_date = min(map(lambda a: a.dateCreated, activities))
        activity_class = Activate.get_activity()
        already_activities_since_min_date = activity_class.query \
                                                           .filter(entity.get_activity_join_filter(),
                                                                   activity_class.dateCreated >= min_date,
                                                                   activity_class.verb == 'update') \
                                                           .all()

        all_activities_since_min_date = sorted(already_activities_since_min_date + activities,
                                               key=lambda activity: activity.dateCreated)

        model = Save.model_from_table_name(entity.__tablename__)
        entity = model.query.get(entity.id)
        merged_datum = merged_datum_from_activities(entity, all_activities_since_min_date)

        database = Activate.get_db()
        database.session.add_all(activities)
        if model.id.key in merged_datum:
            del merged_datum[model.id.key]
        with versioning_manager.disable(database.session):
            entity.modify(merged_datum,
                          with_add=True,
                          with_check_not_soft_deleted=with_check_not_soft_deleted)
            database.session.flush()

    @staticmethod
    def activate(*activities,
                 with_check_not_soft_deleted=True):
        entities = []
        for (entity_identifier, grouped_activities) in groupby(Activate.unknown_activities_from(activities),
                                                               key=lambda activity: activity.entityIdentifier):
            grouped_activities = sorted(grouped_activities,
                                        key=lambda activity: activity.dateCreated)

            first_activity = grouped_activities[0]
            table_name = first_activity.table_name
            model = Save.model_from_table_name(table_name)

            if first_activity.verb == 'delete':
                Activate.activate_deletion(first_activity)
                Activate.activate(*grouped_activities[1:],
                                   with_check_not_soft_deleted=with_check_not_soft_deleted)
                continue

            if model is None:
                errors = ActivityError()
                errors.add_error('tableName', 'model from {} not found'.format(table_name))
                raise errors

            entity = model.query.filter_by(activityIdentifier=entity_identifier) \
                                .first()
            if not entity:
                Activate.activate_insertion(first_activity)
                entities += Activate.activate(*grouped_activities[1:],
                                              with_check_not_soft_deleted=with_check_not_soft_deleted)
                continue

            entities.append(entity)
            Activate.activate_updates(grouped_activities,
                                      entity,
                                      with_check_not_soft_deleted=with_check_not_soft_deleted)
        return entities


    @classmethod
    def models(cls):
        models = Accessor.models()
        Activity = cls.get_activity()
        if Activity:
            models += [Activity]
        return models

    @staticmethod
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

    @staticmethod
    def upgrade(op):
        from sqlalchemy_api_handler.mixins.activity_mixin import ActivityMixin
        db = Activate.get_db()
        versioning_manager.init(db.Model)
        versioning_manager.transaction_cls.__table__.create(op.get_bind())
        class Activity(ActivityMixin,
                       Activate,
                       versioning_manager.activity_cls):
            __table_args__ = {'extend_existing': True}

            id = versioning_manager.activity_cls.id
        Activity.__table__.create(op.get_bind())
        op.add_column('transaction',
                      sa.Column('actor_id',
                                sa.BigInteger()))
