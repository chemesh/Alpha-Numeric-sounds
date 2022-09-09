from django.db import models

# Create your models here.

class Execution(models.Model):
    identifier = models.CharField(max_length=100)
    date = models.DateField()
    song_1 = models.FilePathField()
    song_2 = models.FilePathField()
    result = models.FilePathField()
