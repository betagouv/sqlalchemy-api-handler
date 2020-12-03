import pytest
from datetime import datetime
from uuid import uuid4
from flask_login import login_user
from sqlalchemy import desc, Integer
from sqlalchemy_api_handler import ApiHandler, humanize
from sqlalchemy_api_handler.serialization import as_dict

from tests.conftest import with_delete
from api.models.activity import Activity
from api.models.offer import Offer
from api.models.stock import Stock
from api.models.user import User


class ActivatorTest:
    def test_models(self, app):
        # When
        models = ApiHandler.models()

        # Then
        assert Activity in models

    def test_model_from_name(self, app):
        # When
        GotActivity = ApiHandler.model_from_name('Activity')

        # Then
        assert GotActivity == Activity

    @with_delete
    def test_create_offer_saves_an_insert_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        activity = Activity.query.filter(Activity.changed_data['id'].astext.cast(Integer) == offer.id).one()
        assert offer.activityUuid == activity.uuid
        assert activity.oldDatum == None
        assert activity.transaction == None
        assert activity.verb == 'insert'
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
        assert activity.verb == 'insert'

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
        activity = Activity.query.filter(
            (Activity.tableName == 'offer') &
            (Activity.verb == 'update') &
            (Activity.data['id'].astext.cast(Integer) == offer.id)
        ).one()
        assert activity.verb == 'update'
        assert activity.uuid == offer.activityUuid
        assert {**offer_dict, **modify_dict}.items() <= activity.datum.items()
        assert modify_dict.items() == activity.patch.items()
        assert offer_dict.items() <= activity.oldDatum.items()

    @with_delete
    def test_create_activity_on_not_existing_offer_saves_an_insert_activity(self, app):
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
        assert activity.uuid == offer.activityUuid
        assert activity.verb == 'insert'
        assert patch.items() <= activity.datum.items()
        assert patch.items() <= activity.patch.items()
        assert activity.datum['id'] == humanize(offer.id)
        assert activity.patch['id'] == humanize(offer.id)

    @with_delete
    def test_create_activities_on_existing_offer_saves_none_activities_and_an_update_one(self, app):
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
        third_patch = { 'type': 'fee' }
        third_activity = Activity(dateCreated=datetime.utcnow(),
                                  patch=third_patch,
                                  tableName='offer',
                                  uuid=offer_uuid)

        # When
        ApiHandler.activate(first_activity, second_activity, third_activity)

        # Then
        activities = Activity.query.filter_by(uuid=offer_uuid) \
                                   .order_by(Activity.dateCreated) \
                                   .all()
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        assert len(activities) == 4
        assert activities[0].uuid == offer.activityUuid
        assert activities[0].verb == 'insert'
        assert activities[1].uuid == offer.activityUuid
        assert activities[1].verb == None
        assert activities[1].patch.items() == second_patch.items()
        assert activities[2].uuid == offer.activityUuid
        assert activities[2].verb == None
        assert activities[2].patch.items() == third_patch.items()
        assert activities[3].uuid == offer.activityUuid
        assert activities[3].verb == 'update'
        merged_patch = { 'name': 'bor', 'type': 'fee' }
        assert activities[3].patch.items() == merged_patch.items()
        assert offer.name == 'bor'
        assert offer.type == 'fee'

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
        assert offer.activityUuid == offer_activity.uuid
        assert stock.activityUuid == stock_activity.uuid
        assert stock.offerId == offer.id

    @with_delete
    def test_modify_activity_with_a_second_one_via_same_uuid(self, app):
        # Given
        offer_uuid = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity1 = Activity(dateCreated=datetime.utcnow(),
                                   patch=offer_patch,
                                   tableName='offer',
                                   uuid=offer_uuid)
        ApiHandler.activate(offer_activity1)



        stock_uuid = uuid4()
        stock_patch = { 'offerActivityUuid': offer_uuid, 'price': 3 }
        stock_activity = Activity(dateCreated=datetime.utcnow(),
                                  patch=stock_patch,
                                  tableName='stock',
                                  uuid=stock_uuid)
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        offer_patch = { 'name': 'bor', 'type': 'foo' }
        offer_activity2 = Activity(dateCreated=datetime.utcnow(),
                                   patch=offer_patch,
                                   tableName='offer',
                                   uuid=offer_uuid)

        # When
        ApiHandler.activate(stock_activity, offer_activity2)

        # Then
        offer = Offer.query.filter_by(activityUuid=offer_uuid).one()
        stock = Stock.query.filter_by(activityUuid=stock_uuid).one()
        assert offer.activityUuid == offer_activity2.uuid
        assert stock.activityUuid == stock_activity.uuid
        assert stock.offerId == offer.id

    @with_delete
    def test_get_activity_uuid_of_a_relationship(self, app):
        # Given
        offer = Offer(name='bar', type='foo')
        stock = Stock(price=3, offer=offer)
        ApiHandler.save(offer, stock)

        # When
        offer_activity_uuid = stock.offerActivityUuid

        # Then
        assert offer_activity_uuid == offer.activityUuid
