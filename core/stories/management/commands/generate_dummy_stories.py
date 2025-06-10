from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from stories.models import Story, Comment, StoryLike, CommentLike
from faker import Faker
import random
from datetime import datetime, timedelta

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate dummy stories, comments, and likes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating dummy stories and interactions...')

        # Get all users who can create stories (you might want to filter this)
        users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        # Create stories
        stories_created = 0
        for _ in range(50):  # Create 50 stories
            try:
                author = random.choice(users)
                story = Story.objects.create(
                    author=author,
                    content=fake.paragraph(nb_sentences=random.randint(3, 8)),
                )
                stories_created += 1

                # Create 0-5 comments for each story
                for _ in range(random.randint(0, 5)):
                    commenter = random.choice(users)
                    Comment.objects.create(
                        story=story,
                        author=commenter,
                        content=fake.sentence(),
                    )
                    story.num_of_comments += 1

                # Add random likes to the story
                num_likes = random.randint(0, min(len(users), 10))
                likers = random.sample(users, num_likes)
                for liker in likers:
                    StoryLike.objects.create(
                        story=story,
                        author=liker
                    )
                    story.num_of_likes += 1

                story.save()  # Save the updated counts

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating story: {str(e)}'))

        # Add likes to comments
        comments = Comment.objects.all()
        for comment in comments:
            # Add random likes to comments
            num_likes = random.randint(0, min(len(users), 5))
            likers = random.sample(users, num_likes)
            for liker in likers:
                try:
                    CommentLike.objects.create(
                        comment=comment,
                        author=liker
                    )
                    comment.num_of_likes += 1
                except Exception:
                    continue  # Skip if unique constraint fails
            comment.save()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created:'
            f'\n- {stories_created} stories'
            f'\n- {Comment.objects.count()} comments'
            f'\n- {StoryLike.objects.count()} story likes'
            f'\n- {CommentLike.objects.count()} comment likes'
        ))
