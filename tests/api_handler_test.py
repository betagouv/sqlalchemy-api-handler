import pytest

from sqlalchemy_api_handler import ApiHandler
from tests.conftest import with_delete
from api.models.offer import Offer

class SaveTest():
    @with_delete
    def test_save_offer(self, app):
        # given
        offer_dict = {
            'name': 'bar',
            'type': 'fee'
        }
        offer = Offer(**offer_dict)

        # when
        ApiHandler.save(offer)

        # then
        saved_offer = Offer.query.first()
        for (key, value) in offer_dict.items():
            assert getattr(saved_offer, key) == value
