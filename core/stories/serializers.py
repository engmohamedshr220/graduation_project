from rest_framework import serializers
from .models import Story , Comment , CommentLike, StoryLike

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id','author','content','num_of_likes','num_of_comments','created_at','updated_at']
        

class CommentSerializer(serializers.ModelSerializer):
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



