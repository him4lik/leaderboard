from enum import Enum

class BaseEnumClass(Enum):

    @classmethod
    def get_keys(cls):
        return [x.name for x in cls]

    @classmethod
    def get_values(cls):
        return [x.value for x in cls]

    @classmethod
    def get_key_value(cls):
        return {x.name:x.value for x in cls}

class GenderChoices(BaseEnumClass):
    Male = 'Male'
    Female = 'Female'