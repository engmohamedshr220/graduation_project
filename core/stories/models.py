from django.db import models
import uuid
from accounts.models import User
# Create your models here.

class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_likes = models.IntegerField(default=0)
    num_of_comments = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.username}'s story ({self.id})"

    class Meta:
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
            models.Index(fields=['num_of_likes'])
        ]
        ordering = ['-created_at']

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.story.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['story','author','content'],name='unique_comment')
        ]
        indexes = [
            models.Index(fields=['story']),          # Fetch comments for a story
            models.Index(fields=['author']),         # User's comment history
            models.Index(fields=['created_at']),     # Sort by newest/oldest
        ]
        ordering = ['-created_at']

class StoryLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Like by {self.author.username} on story {self.story.id}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['story','author'],name='unique_like')
        ]
        indexes = [
            models.Index(fields=['story']),          # Count or list likes on a story
            models.Index(fields=['author']),         # What a user liked
            models.Index(fields=['created_at']),     # Activity tracking
        ]
        ordering = ['-created_at']

class CommentLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Like by {self.author.username} on comment {self.comment.id}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['comment','author'],name='unique_comment_like')
        ]
        indexes = [
            models.Index(fields=['comment']),        # Count or list likes on a comment
            models.Index(fields=['author']),         # What a user liked
            models.Index(fields=['created_at']),     # Activity tracking
        ]
        ordering = ['-created_at']