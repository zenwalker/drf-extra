from rest_framework import viewsets


class ModelViewSet(viewsets.ModelViewSet):
    list_serializer = None
    detail_serializer = None
    update_serlalizer = None

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer
        if self.action == 'retrieve':
            return self.detail_serializer
        if self.action in {'create', 'update', 'partial_update'}:
            if self.update_serlalizer:
                return self.update_serlalizer
            return self.detail_serializer
