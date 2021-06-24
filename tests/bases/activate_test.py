# pylint: disable=R0201
# pylint: disable=W0613

from datetime import datetime, timedelta
from uuid import uuid4
import pytest
from sqlalchemy import Integer
from sqlalchemy_api_handler import ApiHandler, humanize
from sqlalchemy_api_handler.bases.errors import JustBeforeActivityNotFound

from tests.conftest import with_delete
from api.models.activity import Activity
from api.models.offer import Offer
from api.models.stock import Stock


def _assert_activity_match_model(patch, activity, offer):
    assert activity.entityIdentifier == offer.activityIdentifier
    assert patch.items() <= activity.datum.items()
    assert patch.items() <= activity.patch.items()


def assert_insert_activity_match_model(patch, activity, offer):
    _assert_activity_match_model(patch, activity, offer)
    assert activity.verb == 'insert'
    assert activity.patch['id'] == humanize(offer.id)


def assert_update_activity_match_model(patch, activity, offer):
    _assert_activity_match_model(patch, activity, offer)
    assert activity.verb == 'update'
    assert activity.oldDatum['id'] == humanize(offer.id)


class ActivateTest:
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
        offer = activity.entity
        offer_activities = offer.__activities__
        assert offer == Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert len(all_activities) == 1
        assert len(offer_activities) == 1
        assert_insert_activity_match_model(patch, offer_activities[0], offer)


    @with_delete
    def test_create_activity_on_not_existing_offers_saves_two_insert_activities(self, app):
        # Given
        offer1_activity_identifier = uuid4()
        patch1 = { 'name': 'bar', 'type': 'foo' }
        activity1 = Activity(dateCreated=datetime.utcnow(),
                             entityIdentifier=offer1_activity_identifier,
                             patch=patch1,
                             tableName='offer')
        offer2_activity_identifier = uuid4()
        patch2 = { 'name': 'bor', 'type': 'fee' }
        activity2 = Activity(dateCreated=datetime.utcnow(),
                             entityIdentifier=offer2_activity_identifier,
                             patch=patch2,
                             tableName='offer')

        # When
        ApiHandler.activate(activity1, activity2)

        # Then
        all_activities = Activity.query.all()
        assert len(all_activities) == 2

        offer1 = activity1.entity
        assert offer1 == Offer.query.filter_by(activityIdentifier=offer1_activity_identifier).one()
        offer1_activities = offer1.__activities__
        assert len(offer1_activities) == 1
        assert_insert_activity_match_model(patch1, offer1_activities[0], offer1)

        offer2 = activity2.entity
        assert offer2 == Offer.query.filter_by(activityIdentifier=offer2_activity_identifier).one()
        offer2_activities = offer2.__activities__
        assert len(offer2_activities) == 1
        assert_insert_activity_match_model(patch2, offer2_activities[0], offer2)


    @with_delete
    def test_create_activities_on_existing_offer_saves_update_activities(self, app):
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
        offer = third_activity.entity
        assert offer == Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        all_activities = Activity.query.all()
        offer_activities = offer.__activities__
        assert len(all_activities) == 3
        assert len(offer_activities) == 3
        assert offer.name == 'bor'
        assert offer.type == 'fee'
        assert_insert_activity_match_model(first_patch, offer_activities[0], offer)
        assert_update_activity_match_model(second_patch, offer_activities[1], offer)
        assert_update_activity_match_model(third_patch, offer_activities[2], offer)

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
        offer = offer_activity2.entity
        stock = stock_activity.entity
        assert offer == Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert stock == Stock.query.filter_by(activityIdentifier=stock_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity2.entityIdentifier
        assert stock.activityIdentifier == stock_activity.entityIdentifier
        assert stock.offerId == offer.id

    @with_delete
    def test_same_insert_activity_should_not_be_recorded_twice(self, app):
        # Given
        offer_activity_identifier = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        date_created = datetime.utcnow()
        offer_activity1 = Activity(dateCreated=date_created,
                                   entityIdentifier=offer_activity_identifier,
                                   patch=offer_patch,
                                   tableName='offer')
        ApiHandler.activate(offer_activity1)
        duplicate_offer_activity = Activity(dateCreated=date_created,
                                            entityIdentifier=offer_activity_identifier,
                                            patch=offer_patch,
                                            tableName='offer')

        # When
        ApiHandler.activate(duplicate_offer_activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity1.entityIdentifier
        assert len(offer.__activities__) == 1

    @with_delete
    def test_same_insert_activity_should_not_be_recorded_twice_from_dict_edition(self, app):
        # Given
        offer_activity_identifier = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity1 = Activity(**{'modelName': 'Offer', 'dateCreated': '2021-03-31T14:18:52.618Z', 'localIdentifier': 'ec510dea-1087-4770-83be-91c2b91a7d05/2021-03-30T12:21:54.540Z', 'localDossierId': 'AEE8EHCP', 'entityIdentifier': str(offer_activity_identifier), 'patch': offer_patch})
        ApiHandler.activate(offer_activity1)
        duplicate_offer_activity = Activity(**{'modelName': 'Offer', 'dateCreated': '2021-03-31T14:18:52.618Z', 'localIdentifier': 'ec510dea-1087-4770-83be-91c2b91a7d05/2021-03-30T12:21:54.540Z', 'localDossierId': 'AEE8EHCP', 'entityIdentifier': str(offer_activity_identifier), 'patch': offer_patch})

        # When
        ApiHandler.activate(duplicate_offer_activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity1.entityIdentifier
        assert len(offer.__activities__) == 1

    @with_delete
    def test_same_update_activity_should_not_be_recorded_twice(self, app):
        # Given
        offer_activity_identifier = uuid4()
        offer_patch = { 'name': 'bar', 'type': 'foo' }
        offer_activity1 = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer_activity_identifier,
                                   patch=offer_patch,
                                   tableName='offer')
        ApiHandler.activate(offer_activity1)

        offer_patch = { 'name': 'bor', 'type': 'foo' }
        date_created = datetime.utcnow()
        offer_activity2 = Activity(dateCreated=date_created,
                                   entityIdentifier=offer_activity_identifier,
                                   patch=offer_patch,
                                   tableName='offer')
        ApiHandler.activate(offer_activity2)
        duplicate_offer_activity = Activity(dateCreated=date_created,
                                            entityIdentifier=offer_activity_identifier,
                                            patch=offer_patch,
                                            tableName='offer')

        # When
        ApiHandler.activate(duplicate_offer_activity)

        # Then
        offer = Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert offer.activityIdentifier == offer_activity2.entityIdentifier
        assert len(offer.__activities__) == 2

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
        offer = activity.entity
        assert offer == Offer.query.filter_by(activityIdentifier=offer_activity_identifier).one()
        assert_insert_activity_match_model(patch, offer.__activities__[0], offer)

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

    @with_delete
    def test_create_delete_activity_with_previous_updated_activities(self, app):
        # Given
        offer = Offer(name='bar', type='foo')
        ApiHandler.save(offer)

        update_activity = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer.activityIdentifier,
                                   modelName='Offer',
                                   patch={'name': 'bor'})

        delete_activity = Activity(dateCreated=datetime.utcnow(),
                                   entityIdentifier=offer.activityIdentifier,
                                   modelName='Offer',
                                   verb='delete')

        # When
        ApiHandler.activate(update_activity, delete_activity)

        # Then
        query_filter = (Activity.data['id'].astext.cast(Integer) == offer.id) & \
                       (Activity.verb == 'delete')
        activity = Activity.query.filter(query_filter).one()
        offers = Offer.query.all()
        assert len(offers) == 0
        assert activity.entityIdentifier == offer.activityIdentifier

    @with_delete
    def test_raise_JustBeforeActivityNotFound_when_update_activity_date_before_insert_activity_date(self, app):
        # Given
        date_created = datetime.utcnow()
        offer_activity_identifier = uuid4()
        first_patch = { 'name': 'bar', 'type': 'foo' }
        first_activity = Activity(dateCreated=date_created,
                                  entityIdentifier=offer_activity_identifier,
                                  patch=first_patch,
                                  tableName='offer')

        ApiHandler.activate(first_activity)

        second_patch = { 'name': 'bor' }
        second_activity = Activity(dateCreated=date_created - timedelta(minutes=1),
                                   entityIdentifier=offer_activity_identifier,
                                   patch=second_patch,
                                   tableName='offer')

        # When + Then
        with pytest.raises(JustBeforeActivityNotFound):
            ApiHandler.activate(second_activity)
