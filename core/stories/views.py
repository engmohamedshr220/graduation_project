from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
import rest_framework.permissions
from .models import Story , Comment , CommentLike, StoryLike
from .serializers import StorySerializer, CommentSerializer, CommentLikeSerializer, StoryLikeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny


class StoryViewset(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    
    
    
    
    def get_permissions(self):
        if self.action in ['list','retrieve','comments']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    @action(detail=True, methods=['post'] , url_path='like', url_name='like')
    def like(self, request, pk=None):
        story = self.get_object()
        like, created = StoryLike.objects.get_or_create(story=story, author=request.user)
        if not created:
            like.delete()
        return Response({'detail': 'Liked'}, status=status.HTTP_200_OK)
    @action(detail=True, methods=['delete'] , url_path='like', url_name='like')
    def unlike(self, request, pk=None):
        story = self.get_object()
        like = StoryLike.objects.filter(story=story, author=request.user).first()
        if like:
            like.delete()
        return Response({'detail': 'Unliked'}, status=status.HTTP_200_OK)
    
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
    
    
    @action(detail=True, methods=['post'], url_path='comment', url_name='comment')
    def comment(self, request, pk=None):
        story = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, story=story)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='comment', url_name='comment')
    def delete_comment(self, request, pk=None):
        story = self.get_object()
        comment = story.comments.filter(id=request.data.get('comment_id')).first()
        if comment:
            comment.delete()
        return Response({'detail': 'Comment deleted'}, status=status.HTTP_200_OK)
    


