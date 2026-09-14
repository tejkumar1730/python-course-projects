from django.db import models
class Project(models.Model):
    title=models.CharField(max_length=120)
    description=models.TextField()
    technology=models.CharField(max_length=120)
    url=models.URLField(blank=True)
    class Meta:
        ordering=['id']
    def __str__(self): return self.title
class ContactMessage(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    message=models.TextField(max_length=3000)
    created=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.name}: {self.created}'
