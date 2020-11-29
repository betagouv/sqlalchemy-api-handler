import inflect
from functools import reduce
from itertools import groupby
from sqlalchemy import BigInteger

from sqlalchemy_api_handler.bases.accessor import Accessor
from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.bases.save import Save
from sqlalchemy_api_handler.utils.datum import relationships_in


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
    def activate(*activities):
        Activity = Activator.get_activity()
        for (uuid, grouped_activities) in groupby(activities, key=lambda activity: activity.uuid):
            grouped_activities = sorted(grouped_activities, key=lambda activity: activity.dateCreated)

            first_activity = grouped_activities[0]
            table_name = first_activity.tableName
            model = Save.model_from_table_name(table_name)
            if model is None:
                errors = ActivityError()
                errors.add_error('tableName', 'model from {} not found'.format(table_name))
                raise errors

            id_key = model.id.property.key
            entity_id = first_activity.old_data.get(id_key) \
                        if first_activity.old_data else None

            if not entity_id:
                entity = model.query.filter_by(activityUuid=uuid).first()
                entity_id = entity.id if entity else None

            if not entity_id:
                entity = model(**relationships_in(first_activity.patch, model))
                entity.activityUuid = uuid
                Save.save(entity)
                insert_activity = Activity.query.filter(
                    (Activity.tableName == table_name) & \
                    (Activity.data[id_key].astext.cast(BigInteger) == entity.id) & \
                    (Activity.verb == 'insert')
                ).one()
                insert_activity.dateCreated = first_activity.dateCreated
                insert_activity.uuid = uuid
                Save.save(insert_activity)

                # want to make as if first_activity was the inser_activity one
                # for such route like operations
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
                Activator.activate(*grouped_activities[1:])
                continue

            min_date = min(map(lambda a: a.dateCreated, grouped_activities))
            already_activities_since_min_date = Activity.query \
                                                        .filter(
                                                            (Activity.tableName == table_name) & \
                                                            (Activity.data[id_key].astext.cast(BigInteger) == entity_id) & \
                                                            (Activity.dateCreated >= min_date)
                                                        ) \
                                                        .all()

            Save.save(*grouped_activities)
            all_activities_since_min_date = sorted(already_activities_since_min_date + grouped_activities,
                                                   key=lambda activity: activity.dateCreated)
            datum = merged_datum_from_activities(all_activities_since_min_date,
                                                 model,
                                                 initial=all_activities_since_min_date[0].datum)
            if model.id.key in datum:
                del datum[model.id.key]
            datum['activityUuid'] = uuid
            entity = model.query.get(entity_id)
            entity.modify(datum)
            Save.save(entity)

    @classmethod
    def models(cls):
        models = Accessor.models()
        Activity = cls.get_activity()
        if Activity:
            models += [Activity]
        return models
