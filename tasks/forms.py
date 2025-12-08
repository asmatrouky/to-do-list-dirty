from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Add new task'}
        )
    )

    priority = forms.BooleanField(
        required=False,
        label="Prioritaire",
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = Task
        fields = ['title', 'complete', 'priority']
