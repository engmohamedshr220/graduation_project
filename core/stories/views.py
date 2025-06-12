from django.shortcuts import render
from  rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
import rest_framework.permissions
from .models import Story , Comment , CommentLike, StoryLike
from .serializers import StorySerializer, CommentSerializer, CommentLikeSerializer, StoryLikeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny


class StoryViewset(ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_serializer_class(self):
        if self.action in ['comment']:
            return CommentSerializer
        return super().get_serializer_class()
    
    
    
    def get_permissions(self):
        if self.action in ['list','retrieve','comments']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    
    @action(detail=True, methods=['post'] , url_path='like', url_name='like')
    def like(self, request, pk=None):
        story = self.get_object()
        like, created = StoryLike.objects.get_or_create(story=story, author=request.user)
        if created:
            story.num_of_likes += 1
            story.save()
            print("Story liked")
        return Response({'detail': 'Liked'}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    @action(detail=True, methods=['delete'] , url_path='like', url_name='like')
    def unlike(self, request, pk=None):
        story = self.get_object()
        like = StoryLike.objects.filter(story=story, author=request.user).first()
        if like:
            like.delete()
        return Response({'detail': 'Unliked'}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'], url_path='likes', url_name='likes')
    def likes(self, request, pk=None):
        story = self.get_object()
        likes = story.likes.all()
        serializer = StoryLikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='comments', url_name='comments')
    def comments(self, request, pk=None):
        story = self.get_object()
        comments = story.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['post','put'], url_path='comment', url_name='comment')
    def comment(self, request, pk=None):
        story = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, story=story)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='comment/(?P<comment_id>[^/.]+)', url_name='comment-delete')
    def delete_comment(self, request, pk=None, comment_id=None):
        story = self.get_object()
        
        try:
            comment = story.comments.get(id=comment_id)
            # Check if the user is the author of the comment
            if comment.author != request.user:
                return Response(
                    {'detail': 'You are not authorized to delete this comment'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            comment.delete()
            return Response(
                {'detail': 'Comment deleted successfully'}, 
                status=status.HTTP_200_OK
            )
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    


