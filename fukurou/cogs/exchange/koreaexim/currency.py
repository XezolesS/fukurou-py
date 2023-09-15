from .data import (
    RESPONSE_ELEMENTS,
    CURRENCIES
)

class Currency:
    """
    Currency data class.
    """

    @property
    def unit(self) -> str:
        return self.__unit

    @property
    def name(self) -> str:
        return self.__name

    @property
    def base_rate(self) -> float:
        return self.__base_rate

    def __init__(self):
        self.__unit = '???'
        self.__name = '???'
        self.__base_rate = 0

    def load(self, obj: dict):
        cur_unit = obj[RESPONSE_ELEMENTS[0]]
        cur_base_rate = float(obj[RESPONSE_ELEMENTS[4]].replace(',', ''))

        # Process units which has base of 100
        if '(100)' in cur_unit:
            cur_unit = cur_unit.replace('(100)', '')
            cur_base_rate /= 100

        self.__unit = cur_unit
        self.__name = obj[RESPONSE_ELEMENTS[1]]
        self.__base_rate = cur_base_rate
