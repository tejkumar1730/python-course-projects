from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
class Student(models.Model):
    roll_number=models.CharField(max_length=30,unique=True)
    name=models.CharField(max_length=120)
    email=models.EmailField()
    course=models.CharField(max_length=120)
    score=models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0),MaxValueValidator(100)])
    enrolled=models.DateField()
    class Meta:
        ordering=['roll_number']
        constraints=[models.CheckConstraint(condition=models.Q(score__gte=0,score__lte=100),name='score_between_0_100')]
    def __str__(self): return f'{self.roll_number} - {self.name}'
