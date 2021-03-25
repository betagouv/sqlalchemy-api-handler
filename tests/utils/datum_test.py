import pytest

from sqlalchemy_api_handler.utils.datum import nesting_datum_from


class DatumTest:
    def test_nesting_datum(self, app):
        # Given
        datum = {
                  'offer.name': 'foo',
                  'offer.offerTags.0.tag.label': 'cir',
                  'offer.offerTags.0.tag.__SEARCH_BY__': 'label',
                  'offer.offerTags.1.tag.label': 'dor',
                  'offer.type': 'bar',
                  'price': 2
                }

        # When
        nesting_datum = nesting_datum_from(datum)

        # Then
        assert nesting_datum == {
            'offer': {
                'name': 'foo',
                'offerTags': [
                    {
                        'tag': {
                            'label': 'cir',
                            '__SEARCH_BY__': 'label'

                        }
                    },
                    {
                        'tag': {
                            'label': 'dor',

                        }
                    }
                ],
                'type': 'bar'
            },
            'price': 2,
        }
