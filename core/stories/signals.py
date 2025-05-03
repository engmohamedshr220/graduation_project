from django.db.models.signals import  post_save ,pre_delete
from django.dispatch import receiver

from .models import Story , Comment , StoryLike, CommentLike


@receiver(post_save, sender=StoryLike)
def update_story_like_count_on_save(sender, instance, created, **kwargs):
    if created:
        instance.story.num_of_likes += 1
        instance.story.save()


@receiver(pre_delete, sender=StoryLike)
def update_story_like_count_on_delete(sender, instance, **kwargs):
    instance.story.num_of_likes -= 1
    instance.story.save()
    

@receiver(post_save, sender=CommentLike)
def update_comment_like_count_on_save(sender, instance, created, **kwargs):
    if created:
        instance.comment.num_of_likes += 1
        instance.comment.save()
    

@receiver(pre_delete, sender=CommentLike)
def update_comment_like_count_on_delete(sender, instance, **kwargs):
    instance.comment.num_of_likes -= 1
    instance.comment.save()