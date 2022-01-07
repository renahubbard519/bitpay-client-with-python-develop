from src.bitpay_sdk.exceptions.refund_exception import RefundException


class RefundCancellationException(RefundException):
    __bitpay_message = "Failed to cancel refund object"
    __bitpay_code = "BITPAY-REFUND-CANCEL"
    __api_code = ""

    def __init__(self, message, code=165, api_code="000000"):
        message = self.__bitpay_code + ": " + self.__bitpay_message + ":" + message
        self.__api_code = api_code
        super.__init__(message, code)

    def get_api_code(self):
        return self.__api_code
