from rest_framework.exceptions import APIException


class FilterException(APIException):
    status_code = 400
