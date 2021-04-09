import pytest
from werkzeug.exceptions import NotFound
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils.humanize import humanize
from sqlalchemy_api_handler.utils.load_or_404 import load_or_404

from tests.conftest import with_delete
from api.models.offer import Offer


class LoadOr404Test:
    @with_delete
    def test_load_entity(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = load_or_404(Offer, humanize(offer1.id))

        # Then
        assert offer1.id == offer2.id

    @with_delete
    def test_404_with_not_existing_id(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        with pytest.raises(NotFound):
            load_or_404(Offer, humanize(offer1.id + 1))

    @with_delete
    def test_404_with_wrong_base_id(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        offer1.id = 6
        ApiHandler.save(offer1)

        # When
        with pytest.raises(NotFound):
            load_or_404(Offer, 'AZ')
