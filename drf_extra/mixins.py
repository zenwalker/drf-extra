class DynamicFieldsSerializerMixin:
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DynamicFieldsViewMixin:
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        fields = None

        if self.request.method == 'GET':
            query_fields = self.request.query_params.get('fields', None)
            if query_fields:
                fields = tuple(query_fields.split(','))

        kwargs['context'] = self.get_serializer_context()
        kwargs['fields'] = fields

        return serializer_class(*args, **kwargs)


class SetterSet(list):
    def execute(self, *args, **kwargs):
        return [i(*args, **kwargs) for i in self]


class SerializerSetterMixin:
    def create(self, validated_data):
        setter_set = self.create_setters(validated_data)
        created_instance = super().create(validated_data)
        setter_set.execute(created_instance)
        return created_instance

    def update(self, instance, validated_data):
        setter_set = self.create_setters(validated_data)
        updated_instance = super().update(instance, validated_data)
        setter_set.execute(updated_instance)
        return updated_instance

    def create_setters(self, validated_data):
        setter_set = SetterSet()
        for key, value in validated_data.copy().items():
            def setter(instance):
                setter_method_name = 'save_' + key
                setter_method = getattr(self, setter_method_name, None)
                if setter_method:
                    return setter_method(instance, value)
            setter_set.append(setter)
            validated_data.pop(key)
        return setter_set
