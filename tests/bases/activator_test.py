from sqlalchemy_api_handler import ApiHandler

from tests.conftest import with_delete
from tests.test_utils.models.activity import Activity
from tests.test_utils.models.user import User


class ActivatorTest:
    @with_delete
    def test_create_user_save_an_insert_activity(self):
        # Given
        user = User(email='foo@foo.com',
                    firstName='Foo',
                    publicName='foo')

        # When
        ApiHandler.save(user)

        # Then
        user = User.query.one()
        print(user)
        activities = Activity.query.all()
        print("MMM", activities)
        assert 2 == 3



        """
        user.modify({
            'email': '{}test.diagnostician0@{}'.format(COMMAND_NAME, EMAIL_HOST),
            'firstName': 'faa',
            'lastName': 'fee'
        })
        dossier = Dossier(inseeCode='fee',
                          number='Mauvais numero',
                          user=user)
        ApiHandler.save(dossier, user)
        dossier.number = '022-AF0032-1'
        ApiHandler.save(dossier)
        dossier_uuid = uuid4()
        first_activity = Activity(dateCreated=datetime.utcnow(),
                                  oldDatum={'dossier_id': humanize(dossier.id)},
                                  patch={'inseeCode': 'foo'},
                                  tableName='dossier',
                                  userId=humanize(user.id),
                                  uuid=dossier_uuid)
        second_activity = Activity(dateCreated=datetime.utcnow(),
                                   oldDatum={'dossier_id': humanize(dossier.id)},
                                   patch={'goodOccupiersCount': 3 },
                                   tableName='dossier',
                                   userId=humanize(user.id),
                                   uuid=dossier_uuid)
        ApiHandler.activate(first_activity, second_activity)
        activities = Activity.query.all()
        print("INSERT ACTIVITY FROM A DOSSIER SAVE", activities[0], activities[0].verb, humanize(dossier.id), activities[0].datum['id'])
        print("UPDATE ACTIVITY FROM A DOSSIER SAVE", activities[1], activities[1].verb, dossier.number, activities[1].patch['number'])
        print("TRANSITORY ACTIVITY FROM A DOSSIER ACTIVATE", activities[2], activities[2].verb, dossier.activityUuid, activities[2].uuid, dossier.inseeCode, activities[2].patch)
        print("TRANSITORY ACTIVITY FROM A DOSSIER ACTIVATE", activities[3], activities[3].verb, dossier.activityUuid, activities[3].uuid, dossier.goodOccupiersCount, activities[3].patch)
        print("UPDATE ACTIVITY FROM A DOSSIER ACTIVATE", activities[4], activities[4].verb, dossier.activityUuid, activities[4].uuid, activities[4].patch)
        """
