from rest_framework import serializers
from .models import Story , Comment , CommentLike, StoryLike

class StorySerializer(serializers.ModelSerializer):
    
    id = serializers.UUIDField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    num_of_likes = serializers.IntegerField( read_only=True)
    num_of_comments = serializers.IntegerField(read_only=True)
    
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "name": obj.author.name,
            "email": obj.author.email,
            "phone": obj.author.phone,
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

    class Meta:
        model = Story
        fields = ['id','author','content','num_of_likes','num_of_comments','created_at','updated_at']
        

class CommentSerializer(serializers.ModelSerializer):
    story =  serializers.UUIDField(read_only = True)
    author = serializers.SerializerMethodField(read_only=True)
    id = serializers.UUIDField(read_only=True)
    num_of_likes = serializers.IntegerField( read_only=True)
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "name": obj.author.name,
            "email": obj.author.email,
            "phone": obj.author.phone,

        }
    class Meta:
        model = Comment
        fields = ['id','story','author','content','num_of_likes','created_at','updated_at']
        
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id','comment','author','created_at']
        
class StoryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryLike
        fields = ['id','story','author','created_at']



