from rest_framework.serializers import ModelSerializer
from .models import ChatMessage

class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'message', 'timestamp', 'is_ai']
        
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'timestamp': {'read_only': True},
            'is_ai': {'read_only': True}
            }