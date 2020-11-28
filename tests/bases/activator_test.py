import pytest
from datetime import datetime
from uuid import uuid4
from flask_login import login_user
from sqlalchemy import Integer
from sqlalchemy_api_handler import ApiHandler, humanize
from sqlalchemy_api_handler.serialization import as_dict

from tests.conftest import with_delete
from api.models.activity import Activity
from api.models.offer import Offer
from api.models.offer import Stock
from api.models.user import User


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
        assert activity.datum['id'] == humanize(offer.id)
        assert activity.patch['id'] == humanize(offer.id)

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

    @with_delete
    def test_create_activity_offer_saves_an_insert_activity(self, app):
        # Given
        offer_uuid = uuid4()
        patch = { 'name': 'bar', 'type': 'foo' }
        activity = Activity(dateCreated=datetime.utcnow(),
                            patch=patch,
                            tableName='offer',
                            uuid=offer_uuid)

        # When
        ApiHandler.activate(activity)

        # Then
        activity = Activity.query.filter_by(uuid=offer_uuid).one()
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        assert activity.verb == 'insert'
        assert patch.items() <= activity.datum.items()
        assert patch.items() <= activity.patch.items()
        assert activity.datum['id'] == humanize(offer.id)
        assert activity.patch['id'] == humanize(offer.id)

    @with_delete
    def test_create_two_activities_offer_saves_an_insert_and_an_update_activity(self, app):
        # Given
        offer_uuid = uuid4()
        first_patch = { 'name': 'bar', 'type': 'foo' }
        first_activity = Activity(dateCreated=datetime.utcnow(),
                                  patch=first_patch,
                                  tableName='offer',
                                  uuid=offer_uuid)
        second_patch = { 'name': 'bor' }
        second_activity = Activity(dateCreated=datetime.utcnow(),
                                   patch=second_patch,
                                   tableName='offer',
                                   uuid=offer_uuid)

        # When
        ApiHandler.activate(first_activity, second_activity)

        # Then
        activities = Activity.query.filter_by(uuid=offer_uuid).all()
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        assert len(activities) == 2
        assert offer.name == 'bor'


    @with_delete
    def test_create_activity_stock_binds_relationship_with_offer(self, app):
        # Given
        offer_uuid = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity = Activity(dateCreated=datetime.utcnow(),
                                  patch=offer_patch,
                                  tableName='offer',
                                  uuid=offer_uuid)
        stock_uuid = uuid4()
        stock_patch = { 'offerActivityUuid': offer_uuid, 'price': 3 }
        stock_activity = Activity(dateCreated=datetime.utcnow(),
                                  patch=stock_patch,
                                  tableName='stock',
                                  uuid=stock_uuid)

        # When
        ApiHandler.activate(offer_activity, stock_activity)

        # Then
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        stock = Stock.query.filter_by(activityUuid=stock_uuid).one()
        assert stock.offerId == offer.id

    @with_delete
    def test_create_activity_with_collection_name(self, app):
        # Given
        offer_uuid = uuid4()
        patch = { 'name': 'bar', 'type': 'foo' }
        activity = Activity(dateCreated=datetime.utcnow(),
                            collectionName='offers',
                            patch=patch,
                            uuid=offer_uuid)

        # When
        ApiHandler.activate(activity)

        # Then
        activity = Activity.query.filter_by(uuid=offer_uuid).one()
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        assert activity.tableName == 'offer'
        assert activity.verb == 'insert'
        assert patch.items() <= activity.datum.items()
        assert patch.items() <= activity.patch.items()
        assert activity.datum['id'] == humanize(offer.id)
        assert activity.patch['id'] == humanize(offer.id)
