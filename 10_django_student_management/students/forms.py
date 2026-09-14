from django import forms
from .models import Student
class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['roll_number','name','email','course','score','enrolled']
        widgets={'enrolled':forms.DateInput(attrs={'type':'date'})}
    def clean_roll_number(self): return self.cleaned_data['roll_number'].strip().upper()
