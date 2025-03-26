from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    pass

class Post(models.Model):
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  date_stamp = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  content = models.TextField()
  
  def total_likes(self):
    return self.likes.count()
  def __str__(self):
    return self.content[:50]
  
class Like(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
  time_stamp = models.DateTimeField(auto_now_add=True)
  class Meta:
    constraints= [
        models.UniqueConstraint(fields=['post', 'user'], name='unique_user_post')
      ]
  def __str__(self):
    return f'{self.user.username} liked {self.post}'
    
class Comment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  text = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Comment by {self.user.username} on {self.post.title}"