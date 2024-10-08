from django.db import models
from django.contrib.auth.models import Group, User
    
class PrayerRequest(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.content
    

class GroupPrayerManager(models.Model):
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class AnsweredPrayer(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE)
    content = models.TextField()
