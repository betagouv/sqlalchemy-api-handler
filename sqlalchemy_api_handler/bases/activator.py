import inflect
from functools import reduce
from itertools import groupby

from sqlalchemy_api_handler.api_errors import ApiErrors
from sqlalchemy_api_handler.bases.save import Save


def merged_datum_from_activities(activities, initial=None):
    return reduce(lambda agg, activity: {**agg, **activity.changed_data},
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
        Save.save(*activities)
        Activity = Activator.get_activity()
        entities = []
        for uuid, grouped_activities in groupby(activities, lambda activity: activity.uuid):
            grouped_activities = list(grouped_activities)

            table_name = grouped_activities[0].table_name
            model = Save.model_from_table_name(table_name)
            if model is None:
                errors = ApiErrors()
                errors.add_error('activity', 'model from {} not found'.format(table_name))
                raise errors



            min_issued_at = min(map(lambda a: a.issued_at, grouped_activities))
            last_activity_with_old_data_since = Activity.query \
                                           .filter(
                                               (Activity.old_data != None) & \
                                               (Activity.issued_at <= min_issued_at) & \
                                               (Activity.uuid == uuid)) \
                                           .order_by(Activity.issued_at.desc()).first()
            if not last_activity_with_old_data_since:
                all_activities_since = Activity.query \
                                               .filter(
                                                   (Activity.issued_at >= min_issued_at) & \
                                                   (Activity.uuid == uuid)) \
                                               .order_by(Activity.issued_at) \
                                               .all()
                created_datum = merged_datum_from_activities(all_activities_since)
                entity = model(**created_datum)
            else:
                all_activities_since = Activity.query \
                                               .filter(
                                                   (Activity.issued_at >= last_activity_with_old_data_since.issued_at) & \
                                                   (Activity.uuid == uuid)) \
                                               .order_by(Activity.issued_at) \
                                               .all()
                modified_datum = merged_datum_from_activities(all_activities_since,
                                                              last_activity_with_old_data_since.old_data)
                entity = last_activity_with_old_data_since.object
                entity.modify(modified_datum)

            entity.activityUuid = uuid
            entities.append(entity)
        Save.save(*entities)
