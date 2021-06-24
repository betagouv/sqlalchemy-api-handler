# pylint: disable=R0201
# pylint: disable=W0613

import pytest
from flask_login import login_user
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils import humanize
from tests.conftest import with_delete

from api.models.activity import Activity
from api.models.offer import Offer
from api.models.user import User


class SaveTest():
    @with_delete
    def test_save_user(self, app):
        # given
        user_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName': 'Marx',
            'lastName': 'Foo',
            'publicName': 'Marx Foo'
        }
        user = User(**user_dict)

        # when
        ApiHandler.save(user)

        # then
        saved_user = User.query.first()
        for (key, value) in user_dict.items():
            assert getattr(saved_user, key) == value

    @with_delete
    def test_create_offer_saves_an_insert_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        all_activities = Activity.query.all()
        offer_activities = offer.__activities__
        insert_offer_activity = offer_activities[0]
        insert_offer_activity_from_query = Activity.query \
            .filter_by(entityIdentifier=offer.activityIdentifier) \
            .one()
        assert len(all_activities) == 1
        assert len(offer_activities) == 1
        assert insert_offer_activity_from_query == insert_offer_activity
        assert offer.activityIdentifier == insert_offer_activity.entityIdentifier
        assert insert_offer_activity.entityInsertedAt == offer.dateCreated
        assert insert_offer_activity.oldDatum == None
        assert insert_offer_activity.transaction == None
        assert insert_offer_activity.verb == 'insert'
        assert offer_dict.items() <= insert_offer_activity.patch.items()
        assert offer_dict.items() <= insert_offer_activity.datum.items()
        assert insert_offer_activity.datum['id'] == humanize(offer.id)
        assert insert_offer_activity.patch['id'] == humanize(offer.id)

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
        all_activities = Activity.query.all()
        offer_activities = offer.__activities__
        insert_offer_activity = offer_activities[0]
        assert len(all_activities) == 1
        assert len(offer_activities) == 1
        assert insert_offer_activity.transaction.actor.id == user.id

    @with_delete
    def test_modify_offer_saves_an_update_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        modify_dict = { 'name': 'bor' }
        offer.modify(modify_dict)

        # When
        ApiHandler.save(offer)

        # Then
        all_activities = Activity.query.all()
        offer_activities = offer.__activities__
        update_offer_activity = offer_activities[1]
        assert len(all_activities) == 2
        assert len(offer_activities) == 2
        assert update_offer_activity.entityIdentifier == offer.activityIdentifier
        assert update_offer_activity.verb == 'update'
        assert {**offer_dict, **modify_dict}.items() <= update_offer_activity.datum.items()
        assert modify_dict.items() == update_offer_activity.patch.items()
        assert offer_dict.items() <= update_offer_activity.oldDatum.items()
