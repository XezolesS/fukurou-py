import json
import requests

from .data import (
    URL,
    CURRENCIES
)

from .currency import Currency

class KoreaExIm:
    """
    ## KoreaExIm Wrapper

    An API wrapper class for Export-Import Bank of Korea (koreaexim.go.kr).
    The base currency for the API is Korean won (KRW).

    한국수출입은행 API의 래퍼 클래스입니다.
    본 API의 기본통화는 한국 원화(KRW)입니다.

    :param str token: API key of koreaexim.go.kr.
    """

    def __init__(self, token: str):
        self.token = token
        self.currencies = {}

    def load(self) -> int:
        """
        Load exchange data from koreaexim.go.kr.
        Loaded data are stored in the instance.

        :returns: `result code`
            '-1' Connection error
            `1` Success
            `2` Data code error
            `3` Verification error
            `4` Daily request limit exceeded
        
        :rtype: int
        """
        response = requests.get(self.__build_url(), timeout=10)

        # Connection check
        if not response.ok:
            return -1

        data = response.json()

        # API response result check
        api_result = data[0]['result']
        if api_result != 1:
            return api_result

        # Instantiate and map currency data
        for obj in data:
            currency = Currency()
            currency.load(obj=obj)

            self.currencies[currency.unit] = currency

        return 1

    def base_rate(self, currency: str) -> float | None:
        """
        Returns base rate of the currency.

        :param str currency: Unit of the currency.

        :returns: Base rate of the currency.
        :rtype: float | None
        """
        if currency not in self.currencies:
            return None

        return self.currencies[currency].base_rate

    def name(self, currency: str) -> str | None:
        """
        Returns name of the currency.

        :param str currency: Unit of the currency.

        :returns: Name of the currency.
        :rtype: str | None
        """
        if currency not in self.currencies:
            return None

        return self.currencies[currency].name

    def exchange(self, source_currency: str, target_currency: str, amount: float) -> float:
        """
        Exchange amount of currency to others.

        :param str source_currency: Unit of the currency to exchange.
        :param str target_currency: Unit of the currency to be exchanged.
        :param float amount: Amount of currency to exchange.

        :returns: Amount of currency to be exchanged. -1 if invalid currency passed.
        :rtype: float
        """

        if source_currency not in CURRENCIES:
            return -1

        if target_currency not in CURRENCIES:
            return -1

        src = self.currencies[source_currency]
        trg = self.currencies[target_currency]

        return (amount * src.base_rate) / trg.base_rate

    def __build_url(self, search_date: str = None, data: str = 'AP01') -> str:
        url = f'{URL}?authkey={self.token}'

        if search_date is not None:
            url += f'&searchdate={search_date}'

        url += f'&data={data}'

        return url
