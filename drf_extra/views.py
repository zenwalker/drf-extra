from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins


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
