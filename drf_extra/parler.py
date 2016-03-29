from rest_framework import serializers
from collections import OrderedDict


class TranslatedFieldsField(serializers.Field):
    def __init__(self, allow_empty=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_empty = allow_empty

    def bind(self, field_name, parent):
        """
        Create translation serializer dynamically.
        """
        super().bind(field_name, parent)
        shared_model = parent.Meta.model
        related_name = self.source or field_name
        translated_model = shared_model._parler_meta[related_name]
        self.serializer_class = create_translated_fields_serializer(
            shared_model, related_name=related_name,
            meta={'fields': translated_model.get_translated_fields()}
        )

    def to_representation(self, value):
        """
        Serialize translated fields.
        Simply iterate over available translations and, for each language,
        delegate serialization logic to the translation model serializer.
        """
        if value is None:
            return

        serializer = self.serializer_class(
            instance=self.parent.instance,
            context=self.context,
            partial=self.parent.partial
        )

        translations = value.all()
        if 'request' in self.context:
            language_codes = self.context['request'].query_params.get('translations')
            if language_codes:
                translations = translations.filter(language_code__in=language_codes.split(','))

        result = OrderedDict()
        for translation in translations:
            result[translation.language_code] = serializer.to_representation(translation)

        return result

    def to_internal_value(self, data):
        """
        Deserialize data from translations fields.
        For each received language, delegate validation logic to
        the translation model serializer.
        """
        if data is None:
            return

        if not isinstance(data, dict):
            self.fail('invalid')
        if not self.allow_empty and len(data) == 0:
            self.fail('empty')

        result, errors = {}, {}
        for lang_code, model_fields in data.items():
            serializer = self.serializer_class(data=model_fields)
            if serializer.is_valid():
                result[lang_code] = serializer.validated_data
            else:
                errors[lang_code] = serializer.errors

        if errors:
            raise serializers.ValidationError(errors)
        return result


class TranslatableModelSerializer(serializers.ModelSerializer):
    """
    Serializer that saves :class:`TranslatedFieldsField` automatically.
    """
    translations = TranslatedFieldsField()

    default_error_messages = dict(serializers.Field.default_error_messages, **{
        'invalid': "Input is not a valid dict.",
        'empty': "This field may not be empty.",
    })

    def save(self, **kwargs):
        """
        Extract the translations and save them after main object save.
        By default all translations will be saved no matter if creating
        or updating an object. Users with more complex needs might define
        their own save and handle translation saving themselves.
        """
        translated_data = self._pop_translated_data()
        instance = super(TranslatableModelSerializer, self).save(**kwargs)
        self.save_translations(instance, translated_data)
        return instance

    def _pop_translated_data(self):
        """
        Separate data of translated fields from other data.
        """
        translated_data = {}
        for meta in self.Meta.model._parler_meta:
            translations = self.validated_data.pop(meta.rel_name, {})
            if translations:
                translated_data[meta.rel_name] = translations
        return translated_data

    def save_translations(self, instance, translated_data):
        """
        Save translation data into translation objects.
        """
        for meta in self.Meta.model._parler_meta:
            translations = translated_data.get(meta.rel_name, {})
            for lang_code, model_fields in translations.items():
                translation = instance._get_translated_model(lang_code, auto_create=True, meta=meta)
                for field, value in model_fields.items():
                    setattr(translation, field, value)
                translation.save()


def create_translated_fields_serializer(shared_model, meta=None, related_name=None, **fields):
    """
    Create a Rest Framework serializer class for a translated fields model.
    :param shared_model: The shared model.
    :type shared_model: :class:`parler.models.TranslatableModel`
    """
    if not related_name:
        translated_model = shared_model._parler_meta.root_model
    else:
        translated_model = shared_model._parler_meta[related_name].model

    if not meta:
        meta = {}
    meta['model'] = translated_model
    meta.setdefault('fields', ['language_code'] + translated_model.get_translated_fields())

    attrs = {}
    attrs.update(fields)
    attrs['Meta'] = type('Meta', (), meta)

    # Dynamically create the serializer class
    return type('{0}Serializer'.format(translated_model.__name__),
                (serializers.ModelSerializer,), attrs)
