from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    """
    Serializer for handling chat requests.
    """
    user_id = serializers.UUIDField()
    chat_id = serializers.UUIDField(required=False, allow_null=True) 
    message = serializers.CharField()