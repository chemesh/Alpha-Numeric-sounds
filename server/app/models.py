from django.db import models


class Execution(models.Model):
    identifier = models.CharField(max_length=100)
    state = models.CharField(max_length=30)
    timestamp = models.DateTimeField()
    song_1 = models.FilePathField()
    song_2 = models.FilePathField()
    result = models.FileField(upload_to=None)

    def __str__(self):
        return self.identifier
