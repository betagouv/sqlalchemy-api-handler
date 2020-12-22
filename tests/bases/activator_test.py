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


    def test_instance_an_activity(self, app):
        # Given
        offer_dict = { 'name': 'bar', 'type': 'foo' }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        stock_activity_identifier = uuid4()

        # When
        activity = Activity(dateCreated=datetime.utcnow(),
                            entityIdentifier=stock_activity_identifier,
                            modelName='Stock',
                            patch={ 'offerId': offer.humanizedId })

        # Then
        assert activity.patch['offerId'] == offer.humanizedId

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
        assert insert_offer_activity.oldDatum == {}
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

    @with_delete
    def test_create_activity_on_not_existing_offer_saves_an_insert_activity(self, app):
        # Given
        offer_activity_identifier = uuid4()
        patch = { 'name': 'bar', 'type': 'foo' }
        activity = Activity(dateCreated=datetime.utcnow(),
                            entityIdentifier=offer_activity_identifier,
                            patch=patch,
                            tableName='offer')

        # When
        ApiHandler.activate(activity)

        # Then
        all_activities = Activity.query.all()
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        offer_activities = offer.__activities__
        insert_offer_activity = offer_activities[0]
        assert len(all_activities) == 1
        assert len(offer_activities) == 1
        assert insert_offer_activity.entityIdentifier == offer.activityIdentifier
        assert insert_offer_activity.verb == 'insert'
        assert patch.items() <= insert_offer_activity.datum.items()
        assert patch.items() <= insert_offer_activity.patch.items()
        assert insert_offer_activity.datum['id'] == humanize(offer.id)
        assert insert_offer_activity.patch['id'] == humanize(offer.id)

    @with_delete
    def test_create_activities_on_existing_offer_saves_none_activities_and_an_update_one(self, app):
        # Given
        offer_activity_identifier = uuid4()
        first_patch = { 'name': 'bar', 'type': 'foo' }
        first_activity = Activity(dateCreated=datetime.utcnow(),
                                  entityIdentifier=offer_activity_identifier,
                                  patch=first_patch,
                                  tableName='offer')
        second_patch = { 'name': 'bor' }
        second_activity = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer_activity_identifier,
                                   patch=second_patch,
                                   tableName='offer')
        third_patch = { 'type': 'fee' }
        third_activity = Activity(dateCreated=datetime.utcnow(),
                                  entityIdentifier=offer_activity_identifier,
                                  patch=third_patch,
                                  tableName='offer')

        # When
        ApiHandler.activate(first_activity, second_activity, third_activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        all_activities = Activity.query.all()
        offer_activities = offer.__activities__
        merged_patch = { 'name': 'bor', 'type': 'fee' }
        assert len(all_activities) == 4
        assert len(offer_activities) == 4
        assert offer_activities[0].entityIdentifier == offer.activityIdentifier
        assert offer_activities[0].verb == 'insert'
        assert offer_activities[0].id == offer_activities[0].id
        assert offer_activities[1].entityIdentifier == offer.activityIdentifier
        assert offer_activities[1].verb == None
        assert offer_activities[1].patch.items() == second_patch.items()
        assert offer_activities[2].entityIdentifier == offer.activityIdentifier
        assert offer_activities[2].verb == None
        assert offer_activities[2].patch.items() == third_patch.items()
        assert offer_activities[3].entityIdentifier == offer.activityIdentifier
        assert offer_activities[3].verb == 'update'
        assert offer_activities[3].patch.items() == merged_patch.items()
        assert offer.name == 'bor'
        assert offer.type == 'fee'

    @with_delete
    def test_create_activity_stock_binds_relationship_with_offer(self, app):
        # Given
        offer_activity_identifier = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity = Activity(dateCreated=datetime.utcnow(),
                                  entityIdentifier=offer_activity_identifier,
                                  patch=offer_patch,
                                  tableName='offer')
        stock_activity_identifier = uuid4()
        stock_patch = { 'offerActivityIdentifier': offer_activity_identifier, 'price': 3 }
        stock_activity = Activity(dateCreated=datetime.utcnow(),
                                  entityIdentifier=stock_activity_identifier,
                                  patch=stock_patch,
                                  tableName='stock')

        # When
        ApiHandler.activate(offer_activity, stock_activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        stock = Stock.query.filter_by(activityIdentifier=stock_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity.entityIdentifier
        assert stock.activityIdentifier == stock_activity.entityIdentifier
        assert stock.offerId == offer.id

    @with_delete
    def test_modify_activity_with_a_second_one_via_same_activity_identifier(self, app):
        # Given
        offer_activity_identifier = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity1 = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer_activity_identifier,
                                   patch=offer_patch,
                                   tableName='offer')
        ApiHandler.activate(offer_activity1)

        stock_activity_identifier = uuid4()
        stock_patch = { 'offerActivityIdentifier': offer_activity_identifier, 'price': 3 }
        stock_activity = Activity(dateCreated=datetime.utcnow(),
                                  entityIdentifier=stock_activity_identifier,
                                  patch=stock_patch,
                                  tableName='stock')
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        offer_patch = { 'name': 'bor', 'type': 'foo' }
        offer_activity2 = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer_activity_identifier,
                                   patch=offer_patch,
                                   tableName='offer')

        # When
        ApiHandler.activate(stock_activity, offer_activity2)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        stock = Stock.query.filter_by(activityIdentifier=stock_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity2.entityIdentifier
        assert stock.activityIdentifier == stock_activity.entityIdentifier
        assert stock.offerId == offer.id


    @with_delete
    def test_create_activity_on_not_existing_offer_with_model_name(self, app):
        # Given
        offer_activity_identifier = uuid4()
        patch = { 'name': 'bar', 'type': 'foo' }
        activity = Activity(dateCreated=datetime.utcnow(),
                            entityIdentifier=offer_activity_identifier,
                            modelName='Offer',
                            patch=patch)

        # When
        ApiHandler.activate(activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        insert_offer_activity = offer.__activities__[0]
        assert insert_offer_activity.entityIdentifier == offer.activityIdentifier
        assert insert_offer_activity.verb == 'insert'
        assert patch.items() <= insert_offer_activity.datum.items()
        assert patch.items() <= insert_offer_activity.patch.items()
        assert insert_offer_activity.datum['id'] == humanize(offer.id)
        assert insert_offer_activity.patch['id'] == humanize(offer.id)

    @with_delete
    def test_create_delete_activity(self, app):
        # Given
        offer = Offer(name='bar', type='foo')
        ApiHandler.save(offer)
        activity = Activity(dateCreated=datetime.utcnow(),
                            entityIdentifier=offer.activityIdentifier,
                            modelName='Offer',
                            verb='delete')

        # When
        ApiHandler.activate(activity)

        # Then
        query_filter = (Activity.data['id'].astext.cast(Integer) == offer.id) & \
                       (Activity.verb == 'delete')
        activity = Activity.query.filter(query_filter).one()
        offers = Offer.query.all()
        assert len(offers) == 0
        assert activity.entityIdentifier == offer.activityIdentifier
