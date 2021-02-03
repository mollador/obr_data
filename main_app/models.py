from django.db import models
from django.utils import timezone

class DataSource(models.Model):
    url = models.URLField(max_length=300)
    edit_date = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    description = models.CharField(max_length=300, default="no data")
    def __str__(self):
        return self.url

class Document(models.Model):
    Caption = models.CharField(max_length=300)
    DocId = models.CharField(max_length=300)
    Description = models.CharField(max_length=1000)
    Department = models.CharField(max_length=300)
    Keywords = models.CharField(max_length=300)
    file_url = models.CharField(max_length=300)
    edit_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.Caption