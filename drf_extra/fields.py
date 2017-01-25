from django.core.files.base import ContentFile
from rest_framework import serializers
import binascii
import base64
import imghdr
import uuid


class Base64FieldMixin:
    default_error_messages = {
        'invalid_file': "Invalid file message.",
        'invalid_file_type': "Invalid file type.",
    }

    allowed_extensions = set()

    def to_internal_value(self, base64_data):
        if ';base64,' in base64_data:
            _, base64_data = base64_data.split(';base64,')

        try:
            decoded_file = base64.b64decode(base64_data)
        except (TypeError, binascii.Error):
            self.fail('invalid_file')

        extension = imghdr.what('file_name', decoded_file)
        if extension not in self.allowed_extensions:
            self.fail('invalid_file_type')

        file_name = '{}.{}'.format(uuid.uuid4(), extension)
        content_file = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(content_file)


class Base64ImageField(Base64FieldMixin, serializers.ImageField):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
