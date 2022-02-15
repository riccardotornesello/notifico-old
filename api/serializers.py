from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=True, allow_blank=False, max_length=1000)
    token = serializers.CharField(
        required=True, allow_blank=False, max_length=32, min_length=32)
