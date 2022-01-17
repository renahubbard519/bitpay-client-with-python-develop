"""
PayoutRecipientUpdate Exception gets raised when it fails to update recipient
"""
from .payout_recipient_exception import PayoutRecipientException


class PayoutRecipientUpdateException(PayoutRecipientException):
    """
    PayoutRecipientUpdateException
    """
    __bitpay_message = "Failed to update payout recipient"
    __bitpay_code = "BITPAY-PAYOUT-RECIPIENT-UPDATE"
    __api_code = ""

    def __init__(self, message, code=195, api_code="000000"):
        """
        Construct the PayoutRecipientUpdateException.

        :param message: The Exception message to throw.
        :param code: [optional] The Exception code to throw.
        :param api_code: [optional] The API Exception code to throw.
        """
        message = self.__bitpay_code + ": " + self.__bitpay_message + ":" + message
        self.__api_code = api_code
        super().__init__(message, code)

    # def get_api_code(self):
    #     return self.__api_code
