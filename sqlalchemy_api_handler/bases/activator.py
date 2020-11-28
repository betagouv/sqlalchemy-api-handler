import inflect
from functools import reduce
from itertools import groupby
from sqlalchemy import BigInteger

from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.bases.save import Save


def merged_datum_from_activities(activities, initial=None):
    return reduce(lambda agg, activity: {**agg, **activity.patch},
                  activities,
                  initial if initial else {})


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
                entity = model(**first_activity.patch)
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
                first_activity.id = insert_activity.id
                first_activity.changed_data = insert_activity.changed_data
                first_activity.transaction = insert_activity.transaction
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
                                                 all_activities_since_min_date[0].datum)
            del datum[model.id.key]
            datum['activityUuid'] = uuid
            entity = model.query.get(entity_id)
            entity.modify(datum)
            Save.save(entity)
