
from django.urls import path 

from rest_framework.routers import DefaultRouter


from .views import StoryViewset
router = DefaultRouter() 
 
 
router.register('stories', StoryViewset, basename='stories')
# router.register('comments', CommentViewset, basename='comments')

urlpatterns = router.urls