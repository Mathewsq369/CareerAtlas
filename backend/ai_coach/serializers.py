from rest_framework import serializers
from .models import Conversation, Message, CoachingPlan, ResourceRecommendation

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_from_ai', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'last_message']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

class ResourceRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceRecommendation
        fields = ['id', 'title', 'description', 'url', 'resource_type', 'relevance_score']

class CoachingPlanSerializer(serializers.ModelSerializer):
    learning_style_name = serializers.CharField(source='learning_style.name', read_only=True)
    personality_type_name = serializers.CharField(source='personality_type.name', read_only=True)
    resources = ResourceRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = CoachingPlan
        fields = [
            'id', 'student', 'personality_type', 'personality_type_name',
            'learning_style', 'learning_style_name', 'goals', 'challenges',
            'resources', 'created_at'
        ]

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)