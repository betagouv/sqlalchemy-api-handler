from tests.test_utils.models.thing_type import ThingType

class ProductType:
    @classmethod
    def is_thing(cls, name: str) -> object:
        for possible_type in list(ThingType):
            if str(possible_type) == name:
                return True

        return False
