from rest_framework import viewsets, generics, mixins, exceptions
from rest_framework.compat import set_rollback
from rest_framework.response import Response


class ModelView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    def get_serializer_class(self):
        if isinstance(self.serializer_class, dict):
            return self.serializer_class[self.request.method.lower()]
        return self.serializer_class


class ModelViewSet(viewsets.ModelViewSet):
    list_serializer = None
    detail_serializer = None
    update_serializer = None
    create_serializer = None

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer

        if self.action == 'retrieve':
            return self.detail_serializer

        if self.action == 'create':
            if self.create_serializer:
                return self.create_serializer
            return self.detail_serializer

        if self.action in {'update', 'partial_update'}:
            if self.update_serializer:
                return self.update_serializer
            return self.detail_serializer


def full_exception_handler(exc, context):
    """
    Transform dict-like error-messages to flat list.
    """
    if isinstance(exc, exceptions.APIException):
        set_rollback()

        data = exc.get_full_details()
        errors = data

        if isinstance(exc.detail, dict):
            errors = []
            for field_name, values in data.items():
                for value in values.copy():
                    if field_name != 'non_field_errors':
                        value['field'] = field_name
                    errors.append(value)

        return Response(errors, status=exc.status_code)

    return None
