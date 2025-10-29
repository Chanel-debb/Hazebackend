from django.db import models

class Vistor(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    phone_number = models.JSONField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    signed_in = models.DateTimeField(null=True, blank=True)
    signed_out = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.fullname
