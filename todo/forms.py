from datetime import datetime, date

from django import forms

from .models import Todo, Task, SubTask


class CreateUpdateTodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = '__all__'


class CreateUpdateTaskForm(forms.ModelForm):
    details = forms.CharField(required=False)
    completion_date = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y'],
        error_messages={'invalid': 'Date is invalid or does not match format DD-MM-YYYY'}
    )

    def save(self, **kwargs):
        task = super(CreateUpdateTaskForm, self).save(commit=False)
        if kwargs.get('todo'):
            task.todo = kwargs.get('todo')
        task.save()

        return task


    class Meta:
        model = Task
        fields = ('content', 'details', 'is_completed', 'is_subtask', 'completion_date')

