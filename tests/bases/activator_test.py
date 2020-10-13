import pytest
from flask_login import login_user
from sqlalchemy import Integer
from sqlalchemy_api_handler import ApiHandler, humanize
from sqlalchemy_api_handler.serialization import as_dict

from tests.conftest import with_delete
from tests.test_utils.models.activity import Activity, versioning_manager
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.user import User


class ActivatorTest:
    @with_delete
    def test_create_offer_saves_an_insert_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        activity = Activity.query.filter(Activity.changed_data['id'].astext.cast(Integer) == offer.id).one()
        assert activity.verb == 'insert'
        assert activity.oldDatum == None
        assert activity.transaction == None
        assert offer_dict.items() <= activity.patch.items()
        assert offer_dict.items() <= activity.datum.items()


    @with_delete
    def test_create_offer_with_login_user_saves_an_insert_activity_with_transaction(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)
        user = User(email='fee@bar.com', firstName='fee', publicName='foo')
        ApiHandler.save(user)
        login_user(user)

        # When
        ApiHandler.save(offer)

        # Then
        activity = Activity.query.filter(Activity.changed_data['id'].astext.cast(Integer) == offer.id).one()
        assert activity.transaction.actor.id == user.id

    @with_delete
    def test_create_offer_saves_an_insert_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        modify_dict = { 'name': 'bor' }
        offer.modify(modify_dict)

        # When
        ApiHandler.save(offer)

        # Then
        activity = Activity.query.filter(
            (Activity.tableName == 'offer') &
            (Activity.verb == 'update') &
            (Activity.data['id'].astext.cast(Integer) == offer.id)
        ).one()
        assert {**offer_dict, **modify_dict}.items() <= activity.datum.items()
        assert modify_dict.items() == activity.patch.items()
        assert offer_dict.items() <= activity.oldDatum.items()

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
