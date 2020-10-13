from datetime import datetime, timedelta
import pytest
from sqlalchemy_api_handler.serialization import serialize

from api.models.offer import Offer, ThingType
from api.models.time_interval import TimeInterval
from api.models.stock import Stock

time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()


class SerializeTest:
    def test_on_datetime_list_returns_string_with_date_in_ISO_8601_list(self):
        # Given
        offer = Offer()
        stock = Stock()
        stock.offer = offer
        stock.beginningDatetime = now
        stock.endDatetime = now + timedelta(hours=3)
        offer.stocks = [stock]

        # When
        serialized_list = serialize(offer.dateRange)

        # Then
        for date in serialized_list:
            self._assert_is_in_ISO_8601_format(date)

    def test_on_enum_returns_dict_with_enum_value(self):
        # Given
        enum = ThingType.JEUX

        # When
        serialized_enum = serialize(enum)

        # Then
        assert serialized_enum == {
            'conditionalFields': [],
            'proLabel': 'Jeux (support physique)',
            'appLabel': 'Support physique',
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': 'Jouer',
            'description': 'Résoudre l’énigme d’un jeu de piste dans votre ville ? '
                           'Jouer en ligne entre amis ? '
                           'Découvrir cet univers étrange avec une manette ?',
            'isActive': False
        }

    def _assert_is_in_ISO_8601_format(self, date_text):
        try:
            format_string = '%Y-%m-%dT%H:%M:%S.%fZ'
            datetime.strptime(date_text, format_string)
        except TypeError:
            assert False, 'La date doit être un str'
        except ValueError:
            assert False, 'La date doit être au format ISO 8601 %Y-%m-%dT%H:%M:%S.%fZ'
